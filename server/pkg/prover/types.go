// Package prover provides an interface and implementation for running Lean proofs.
package prover

import "time"

type ProofStatus string

const (
	ProofStatusFinished ProofStatus = "finished"
	ProofStatusError    ProofStatus = "error"
)

// Config holds the application-level configuration for the prover.
type Config struct {
	LeanExecutable string
	LeanWorkspace  string
	Concurrency    int // Maximum number of concurrent proof executions
}

// ProofConfig holds the configuration for a single proof execution.
type ProofConfig struct {
	Timeout       time.Duration `json:"timeout"`
	CPUTimeLimit  time.Duration `json:"cpu_time_limit"`
	MemoryLimit   uint64        `json:"memory_limit"`    // Virtual memory limit in bytes
	StackLimit    uint64        `json:"stack_limit"`     // Stack size limit in bytes
	FileSizeLimit uint64        `json:"file_size_limit"` // Maximum file size limit in bytes
	NumFileLimit  uint64        `json:"num_file_limit"`  // Maximum number of open files
	AllTactics    bool          `json:"all_tactics"`
	AST           bool          `json:"ast"`
	Tactics       bool          `json:"tactics"`
	Premises      bool          `json:"premises"`
}

// ProofResult holds the outcome of a proof execution.
type ProofResult struct {
	ProofID      string      `json:"proof_id"`
	Success      bool        `json:"success"`
	Status       ProofStatus `json:"status"`
	Result       any         `json:"result"`
	ErrorMessage string      `json:"error_message,omitempty"`
}
