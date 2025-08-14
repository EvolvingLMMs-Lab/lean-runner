// Package prover provides an interface and implementation for running Lean proofs.
package prover

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os/exec"
	"syscall"

	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"github.com/google/uuid"
	"go.uber.org/zap"
	"golang.org/x/sync/semaphore"
	"golang.org/x/sys/unix"
)

// Prover is an interface that defines the behavior for executing proofs.
type Prover interface {
	Execute(
		ctx context.Context, // context for handling timeouts and cancellations
		proofCode string, // the proof code to execute
		config ProofConfig, // the configuration for the proof
	) (*ProofResult, error)
}

type leanProver struct {
	config Config
	sem    *semaphore.Weighted // Semaphore to control concurrency
}

// NewLeanProver creates a new Lean prover with the given configuration.
func NewLeanProver(config Config) Prover {
	// If concurrency is not set or invalid, use default value of 1
	concurrency := config.Concurrency
	if concurrency <= 0 {
		concurrency = 1
	}

	return &leanProver{
		config: config,
		sem:    semaphore.NewWeighted(int64(concurrency)),
	}
}

// setResourceLimits applies resource limits to the specified process using unix.Prlimit.
// pid is the process ID to apply limits to (0 for current process).
func setResourceLimits(pid int, config ProofConfig) error {
	// Set CPU time limit
	if config.CPUTimeLimit > 0 {
		cpuLimit := uint64(config.CPUTimeLimit.Seconds())
		cpuRlimit := unix.Rlimit{
			Cur: cpuLimit,
			Max: cpuLimit,
		}
		if err := unix.Prlimit(pid, unix.RLIMIT_CPU, &cpuRlimit, nil); err != nil {
			return fmt.Errorf("failed to set CPU time limit: %w", err)
		}
	}

	// Set virtual memory limit
	if config.MemoryLimit > 0 {
		memRlimit := unix.Rlimit{
			Cur: config.MemoryLimit,
			Max: config.MemoryLimit,
		}
		if err := unix.Prlimit(pid, unix.RLIMIT_AS, &memRlimit, nil); err != nil {
			return fmt.Errorf("failed to set memory limit: %w", err)
		}
	}

	// Set stack size limit
	if config.StackLimit > 0 {
		stackRlimit := unix.Rlimit{
			Cur: config.StackLimit,
			Max: config.StackLimit,
		}
		if err := unix.Prlimit(pid, unix.RLIMIT_STACK, &stackRlimit, nil); err != nil {
			return fmt.Errorf("failed to set stack limit: %w", err)
		}
	}

	// Set file size limit
	if config.FileSizeLimit > 0 {
		fileSizeRlimit := unix.Rlimit{
			Cur: config.FileSizeLimit,
			Max: config.FileSizeLimit,
		}
		if err := unix.Prlimit(pid, unix.RLIMIT_FSIZE, &fileSizeRlimit, nil); err != nil {
			return fmt.Errorf("failed to set file size limit: %w", err)
		}
	}

	// Set number of open files limit
	if config.NumFileLimit > 0 {
		noFileRlimit := unix.Rlimit{
			Cur: config.NumFileLimit,
			Max: config.NumFileLimit,
		}
		if err := unix.Prlimit(pid, unix.RLIMIT_NOFILE, &noFileRlimit, nil); err != nil {
			return fmt.Errorf("failed to set number of files limit: %w", err)
		}
	}

	return nil
}

// Execute runs the Lean proof, corresponding to the `execute` method in Python.
// It uses a `context.Context` for handling timeouts and cancellations, which is
// the standard Go pattern for managing long-running operations.
func (p *leanProver) Execute(ctx context.Context, proofCode string, config ProofConfig) (*ProofResult, error) {
	proofIDObj, err := uuid.NewV7()
	if err != nil {
		logger.Error("Failed to generate proof ID", zap.Error(err))
		logger.Info("Falling back to UUIDv4")
		proofIDObj = uuid.New()
	}

	proofID := proofIDObj.String()

	// Acquire semaphore to control concurrency
	if err := p.sem.Acquire(ctx, 1); err != nil {
		return &ProofResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to acquire execution slot: %v", err),
			Result:       map[string]string{"status": "concurrency_limit_reached"},
			ProofID:      proofID,
			Status:       ProofStatusError,
		}, nil
	}
	defer p.sem.Release(1)

	ctx, cancel := context.WithTimeout(ctx, config.Timeout)
	defer cancel()

	commandPayload := struct {
		Cmd        string `json:"cmd"`
		AllTactics bool   `json:"allTactics"`
		AST        bool   `json:"ast"`
		Tactics    bool   `json:"tactics"`
		Premises   bool   `json:"premises"`
	}{
		Cmd:        proofCode,
		AllTactics: config.AllTactics,
		AST:        config.AST,
		Tactics:    config.Tactics,
		Premises:   config.Premises,
	}

	inputJSON, err := json.Marshal(commandPayload)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal command payload: %w", err)
	}

	// Create the command with the context.
	logger.Info("Executing command", zap.String("command", p.config.LeanExecutable), zap.String("workspace", p.config.LeanWorkspace))
	cmd := exec.CommandContext(ctx, p.config.LeanExecutable, "exe", "repl")
	cmd.Dir = p.config.LeanWorkspace

	// Set memory limits, analogous to `preexec_fn` in Python.
	// This is done by setting system process attributes.
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Setpgid: true, // Run in a new process group
	}

	// Set up stdin, stdout, and stderr pipes.
	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to get stdin pipe: %w", err)
	}
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to get stdout pipe: %w", err)
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to get stderr pipe: %w", err)
	}

	// Start the command.
	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start lean process: %w", err)
	}

	// Apply resource limits to the child process.
	if err := setResourceLimits(cmd.Process.Pid, config); err != nil {
		// If setting limits fails, kill the process and return error.
		if killErr := cmd.Process.Kill(); killErr != nil {
			logger.Warn("Failed to kill process after failing to set resource limits", zap.Error(killErr))
		}
		return nil, fmt.Errorf("failed to set resource limits: %w", err)
	}

	// Write the JSON input to the process's stdin in a separate goroutine.
	go func() {
		defer stdin.Close()
		_, err := stdin.Write(inputJSON)
		if err != nil {
			logger.Warn("Failed to write to lean process stdin", zap.Error(err))
		}
	}()

	// Read stdout and stderr.
	stdoutBytes, _ := json.Marshal(stdout)
	stderrBytes, _ := json.Marshal(stderr)

	// Wait for the command to finish.
	err = cmd.Wait()

	// --- Error Handling ---

	// Check for timeout.
	if ctx.Err() == context.DeadlineExceeded {
		return &ProofResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Process timed out after %s", config.Timeout),
			Result:       map[string]string{"status": "timeout"},
			ProofID:      proofID,
			Status:       ProofStatusError,
		}, nil
	}

	// Check for other execution errors (e.g., non-zero exit code).
	if err != nil {
		var exitErr *exec.ExitError
		if errors.As(err, &exitErr) {
			// Process exited with a non-zero status.
			// Check if it was killed by a signal indicating resource limit exceeded.
			if exitErr.Sys().(syscall.WaitStatus).Signaled() {
				signal := exitErr.Sys().(syscall.WaitStatus).Signal()
				switch signal {
				case syscall.SIGKILL:
					// Could be OOM killer or memory limit exceeded
					return &ProofResult{
						Success:      false,
						ErrorMessage: fmt.Sprintf("Process was killed (SIGKILL) - likely memory limit exceeded (%d bytes)", config.MemoryLimit),
						Result:       map[string]string{"status": "memory_limit_exceeded"},
						ProofID:      proofID,
						Status:       ProofStatusError,
					}, nil
				case syscall.SIGXCPU:
					// CPU time limit exceeded
					return &ProofResult{
						Success:      false,
						ErrorMessage: fmt.Sprintf("Process exceeded CPU time limit (%s)", config.CPUTimeLimit),
						Result:       map[string]string{"status": "cpu_time_limit_exceeded"},
						ProofID:      proofID,
						Status:       ProofStatusError,
					}, nil
				case syscall.SIGXFSZ:
					// File size limit exceeded
					return &ProofResult{
						Success:      false,
						ErrorMessage: fmt.Sprintf("Process exceeded file size limit (%d bytes)", config.FileSizeLimit),
						Result:       map[string]string{"status": "file_size_limit_exceeded"},
						ProofID:      proofID,
						Status:       ProofStatusError,
					}, nil
				case syscall.SIGSEGV:
					// Segmentation fault - could be stack overflow
					return &ProofResult{
						Success:      false,
						ErrorMessage: fmt.Sprintf("Process crashed with segmentation fault - possible stack overflow (stack limit: %d bytes)", config.StackLimit),
						Result:       map[string]string{"status": "segmentation_fault"},
						ProofID:      proofID,
						Status:       ProofStatusError,
					}, nil
				default:
					// Other signals
					return &ProofResult{
						Success:      false,
						ErrorMessage: fmt.Sprintf("Process was killed by signal %v", signal),
						Result:       map[string]any{"status": "process_killed", "signal": signal.String()},
						ProofID:      proofID,
						Status:       ProofStatusError,
					}, nil
				}
			}
			// Other exit errors.
			return &ProofResult{
				Success:      false,
				ErrorMessage: fmt.Sprintf("Process exited with code %d: %s", exitErr.ExitCode(), string(stderrBytes)),
				Result:       map[string]any{"status": "process_error", "return_code": exitErr.ExitCode()},
				ProofID:      proofID,
				Status:       ProofStatusError,
			}, nil
		}
		// Other kinds of errors (e.g., executable not found).
		return nil, fmt.Errorf("lean process execution failed: %w", err)
	}

	// --- Result Processing ---

	var resultData any
	if err := json.Unmarshal(stdoutBytes, &resultData); err != nil {
		// Handle cases where the output is not valid JSON.
		return &ProofResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Error parsing JSON from Lean: %v", err),
			Result: map[string]string{
				"raw_output":          string(stdoutBytes),
				"parse_error_message": err.Error(),
			},
			ProofID: proofID,
			Status:  ProofStatusError,
		}, nil
	}

	// Process the result to determine final success, like `_handle_result` in Python.
	processedResult, success := handleResult(resultData)

	return &ProofResult{
		Success:      success,
		Result:       processedResult,
		ErrorMessage: string(stderrBytes),
		ProofID:      proofID,
		Status:       ProofStatusFinished,
	}, nil
}

// handleResult processes the raw result from Lean to determine success.
// This is a private helper function, analogous to `_handle_result` in Python.
func handleResult(result any) (any, bool) {
	resultMap, ok := result.(map[string]any)
	if !ok {
		// If the result is not a map, we can't inspect it for messages.
		// Assume success unless there were other errors.
		return resultMap, true
	}

	messages, ok := resultMap["messages"].([]any)
	if !ok {
		return resultMap, true
	}

	var finalMessages []any
	hasError := false
	for _, msg := range messages {
		msgMap, ok := msg.(map[string]any)
		if !ok {
			finalMessages = append(finalMessages, msg)
			continue
		}
		if severity, ok := msgMap["severity"].(string); ok && severity == "error" {
			hasError = true
		}
		// In this version, we keep all messages, but you could filter warnings here.
		finalMessages = append(finalMessages, msgMap)
	}

	resultMap["messages"] = finalMessages
	return resultMap, !hasError
}
