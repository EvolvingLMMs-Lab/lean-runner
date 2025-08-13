// Package main demonstrates how to control prover concurrency.
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/EvolvingLMMs-Lab/lean-runner/server/pkg/prover"
)

func main() {
	// Example 1: Create a prover with limited concurrency
	config := prover.Config{
		LeanExecutable: "lean",
		LeanWorkspace:  "./workspace",
		Concurrency:    2, // Only allow 2 concurrent proof executions
	}

	p := prover.NewLeanProver(config)

	// Example 2: Execute multiple proofs concurrently
	// Only 2 will run simultaneously due to concurrency limit
	proofCode := `
theorem example : 1 + 1 = 2 := by simp
`

	proofConfig := prover.ProofConfig{
		Timeout:      30 * time.Second,
		CPUTimeLimit: 10 * time.Second,
		MemoryLimit:  1024 * 1024 * 1024, // 1GB
		AllTactics:   false,
		AST:          false,
		Tactics:      false,
		Premises:     false,
	}

	// Launch multiple goroutines to test concurrency control
	fmt.Println("Launching 5 concurrent proof executions (max 2 concurrent)")

	for i := 0; i < 5; i++ {
		go func(id int) {
			ctx := context.Background()
			fmt.Printf("Starting proof %d\n", id)

			result, err := p.Execute(ctx, proofCode, proofConfig)
			if err != nil {
				log.Printf("Proof %d failed: %v", id, err)
				return
			}

			fmt.Printf("Proof %d completed: success=%v\n", id, result.Success)
		}(i)
	}

	// Wait for all proofs to complete
	time.Sleep(10 * time.Second)
	fmt.Println("All proofs completed")
}
