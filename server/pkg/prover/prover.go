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
}

// NewLeanProver creates a new Lean prover with the given configuration.
func NewLeanProver(config Config) Prover {
	return &leanProver{
		config: config,
	}
}

// Execute runs the Lean proof, corresponding to the `execute` method in Python.
// It uses a `context.Context` for handling timeouts and cancellations, which is
// the standard Go pattern for managing long-running operations.
func (p *leanProver) Execute(ctx context.Context, proofCode string, config ProofConfig) (*ProofResult, error) {
	proofID := uuid.New().String()

	ctx, cancel := context.WithTimeout(ctx, config.Timeout)
	defer cancel()

	commandPayload := struct {
		Cmd        string   `json:"cmd"`
		AllTactics bool     `json:"allTactics"`
		AST        bool     `json:"ast"`
		Tactics    []string `json:"tactics"`
		Premises   []string `json:"premises"`
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
	cmd := exec.CommandContext(ctx, p.config.LeanExecutable, "exe", "repl")
	cmd.Dir = p.config.LeanWorkspace

	// Set memory limits, analogous to `preexec_fn` in Python.
	// This is done by setting system process attributes.
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Setpgid: true, // Run in a new process group
		// Rlimit: &syscall.Rlimit{
		// 	Cur: uint64(config.MemoryLimitMB * 1024 * 1024), // Soft limit
		// 	Max: uint64(config.MemoryLimitMB * 1024 * 1024), // Hard limit
		// },
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
		}, nil
	}

	// Check for other execution errors (e.g., non-zero exit code).
	if err != nil {
		var exitErr *exec.ExitError
		if errors.As(err, &exitErr) {
			// Process exited with a non-zero status.
			// Check if it was killed (e.g., by OOM killer).
			if exitErr.Sys().(syscall.WaitStatus).Signaled() && exitErr.Sys().(syscall.WaitStatus).Signal() == syscall.SIGKILL {
				return &ProofResult{
					Success:      false,
					ErrorMessage: fmt.Sprintf("Process was killed due to memory limit (%d MB)", config.MemoryLimitMB),
					Result:       map[string]string{"status": "memory_limit_exceeded"},
					ProofID:      proofID,
				}, nil
			}
			// Other exit errors.
			return &ProofResult{
				Success:      false,
				ErrorMessage: fmt.Sprintf("Process exited with code %d: %s", exitErr.ExitCode(), string(stderrBytes)),
				Result:       map[string]any{"status": "process_error", "return_code": exitErr.ExitCode()},
				ProofID:      proofID,
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
		}, nil
	}

	// Process the result to determine final success, like `_handle_result` in Python.
	processedResult, success := handleResult(resultData)

	return &ProofResult{
		Success:      success,
		Result:       processedResult,
		ErrorMessage: string(stderrBytes),
		ProofID:      proofID,
	}, nil
}

// handleResult processes the raw result from Lean to determine success.
// This is a private helper function, analogous to `_handle_result` in Python.
func handleResult(result any) (any, bool) {
	resultMap, ok := result.(map[string]any)
	if !ok {
		// If the result is not a map, we can't inspect it for messages.
		// Assume success unless there were other errors.
		return result, true
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
