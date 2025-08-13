// Package prover provides an interface and implementation for running Lean proofs.
package prover

import "time"

// Status represents the execution status of a proof.
// It's a custom string type, similar to an Enum in Python.
type Status string

const (
	StatusFinished Status = "FINISHED"
	StatusError    Status = "ERROR"
)

// Config holds the application-level configuration for the prover.
// This corresponds to the `config` object passed in Python.
type Config struct {
	LeanExecutable string
	LeanWorkspace  string
}

// ProofConfig holds the configuration for a single proof execution.
// This corresponds to the `LeanProofConfig` class in Python.
type ProofConfig struct {
	Timeout       time.Duration `json:"timeout"`
	MemoryLimitMB int           `json:"memory_limit_mb"`
	AllTactics    bool          `json:"all_tactics"`
	AST           bool          `json:"ast"`
	Tactics       []string      `json:"tactics"`
	Premises      []string      `json:"premises"`
}

// ProofResult holds the outcome of a proof execution.
// This corresponds to the `LeanProofResult` class in Python.
type ProofResult struct {
	Success      bool   `json:"success"`
	Status       Status `json:"status"`
	Result       any    `json:"result"` // Use 'any' (or interface{}) for flexible JSON data
	ErrorMessage string `json:"error_message,omitempty"`
	ProofID      string `json:"proof_id"`
}
