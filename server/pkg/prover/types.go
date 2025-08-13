// Package prover provides an interface and implementation for running Lean proofs.
package prover

import "time"

// Status represents the execution status of a proof.
type Status string

const (
	StatusFinished Status = "FINISHED"
	StatusError    Status = "ERROR"
)

// Config holds the application-level configuration for the prover.
type Config struct {
	LeanExecutable string
	LeanWorkspace  string
}

// ProofConfig holds the configuration for a single proof execution.
type ProofConfig struct {
	Timeout       time.Duration `json:"timeout"`
	MemoryLimitMB int           `json:"memory_limit_mb"`
	AllTactics    bool          `json:"all_tactics"`
	AST           bool          `json:"ast"`
	Tactics       []string      `json:"tactics"`
	Premises      []string      `json:"premises"`
}

// ProofResult holds the outcome of a proof execution.
type ProofResult struct {
	Success      bool   `json:"success"`
	Status       Status `json:"status"`
	Result       any    `json:"result"`
	ErrorMessage string `json:"error_message,omitempty"`
	ProofID      string `json:"proof_id"`
}
