// Package prover provides an interface and implementation for running Lean proofs.
package prover

import (
	"context"
	"io"
	"os/exec"
	"sync"
	"syscall"

	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"go.uber.org/zap"
)

// leanProcess manages a single, long-running `lean exe repl` process.
type leanProcess struct {
	cmd    *exec.Cmd
	stdin  io.WriteCloser
	stdout io.ReadCloser
	stderr io.ReadCloser
	mu     sync.Mutex
}

// newLeanProcess creates and starts a new `lean exe repl` process.
func newLeanProcess(leanExecutable, leanWorkspace string) (*leanProcess, error) {
	cmd := exec.Command(leanExecutable, "exe", "repl")
	cmd.Dir = leanWorkspace
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Setpgid: true, // Run in a new process group
	}

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, err
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return nil, err
	}

	if err := cmd.Start(); err != nil {
		return nil, err
	}

	return &leanProcess{
		cmd:    cmd,
		stdin:  stdin,
		stdout: stdout,
		stderr: stderr,
	}, nil
}

// execute sends a command to the Lean process and reads the response.
func (lp *leanProcess) execute(ctx context.Context, inputJSON []byte, config ProofConfig) ([]byte, []byte, error) {
	lp.mu.Lock()
	defer lp.mu.Unlock()

	// Apply resource limits to the child process.
	if err := setResourceLimits(lp.cmd.Process.Pid, config); err != nil {
		// If setting limits fails, kill the process and return error.
		if killErr := lp.cmd.Process.Kill(); killErr != nil {
			logger.Warn("Failed to kill process after failing to set resource limits", zap.Error(killErr))
		}
		return nil, nil, err
	}

	// Write the JSON input to the process's stdin.
	if _, err := lp.stdin.Write(inputJSON); err != nil {
		return nil, nil, err
	}

	// Read stdout and stderr in separate goroutines to avoid blocking
	var stdoutBytes, stderrBytes []byte
	var stdoutErr, stderrErr error

	done := make(chan struct{})
	go func() {
		defer close(done)
		stdoutBytes, stdoutErr = io.ReadAll(lp.stdout)
	}()

	go func() {
		stderrBytes, stderrErr = io.ReadAll(lp.stderr)
	}()

	// Wait for output reading to complete
	<-done

	if stdoutErr != nil {
		logger.Warn("Failed to read stdout", zap.Error(stdoutErr))
	}
	if stderrErr != nil {
		logger.Warn("Failed to read stderr", zap.Error(stderrErr))
	}

	return stdoutBytes, stderrBytes, nil
}

// close terminates the Lean process.
func (lp *leanProcess) close() error {
	return lp.cmd.Process.Kill()
}
