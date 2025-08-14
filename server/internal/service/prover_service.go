package service

import (
	"context"
	"fmt"
	"time"

	pb "github.com/EvolvingLMMs-Lab/lean-runner/server/gen/go/proto"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/config"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/pkg/prover"
	"go.uber.org/zap"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/structpb"
)

type ProverService struct {
	pb.UnimplementedProveServiceServer
	prover prover.Prover
}

// NewProverService creates a new ProverService with the given configuration.
func NewProverService(cfg *config.Config) *ProverService {
	proverConfig := prover.Config{
		LeanExecutable: cfg.Lean.Executable,
		LeanWorkspace:  cfg.Lean.Workspace,
		Concurrency:    cfg.Lean.Concurrency,
	}

	p := prover.NewLeanProver(proverConfig)

	logger.Info("ProverService initialized",
		zap.String("lean_executable", proverConfig.LeanExecutable),
		zap.String("lean_workspace", proverConfig.LeanWorkspace),
		zap.Int("concurrency", proverConfig.Concurrency))

	return &ProverService{
		prover: p,
	}
}

// CheckProof handles proof checking requests.
func (s *ProverService) CheckProof(ctx context.Context, req *pb.CheckProofRequest) (*pb.ProofResult, error) {
	if req == nil {
		return nil, status.Errorf(codes.InvalidArgument, "request cannot be nil")
	}

	if req.Proof == "" {
		return nil, status.Errorf(codes.InvalidArgument, "proof code cannot be empty")
	}

	logger.Debug("Received proof request",
		zap.String("proof", req.Proof))

	// Convert protobuf ProofConfig to prover.ProofConfig
	proofConfig, err := convertProofConfig(req.Config)
	if err != nil {
		return nil, status.Errorf(codes.InvalidArgument, "invalid proof config: %v", err)
	}

	logger.Debug("Executing proof",
		zap.String("proof_length", fmt.Sprintf("%d chars", len(req.Proof))),
		zap.Duration("timeout", proofConfig.Timeout))

	// Execute the proof
	result, err := s.prover.Execute(ctx, req.Proof, *proofConfig)
	if err != nil {
		logger.Error("Failed to execute proof", zap.Error(err))
		return nil, status.Errorf(codes.Internal, "proof execution failed: %v", err)
	}

	// Convert result to protobuf format
	pbResult, err := convertToProtoResult(result)
	if err != nil {
		logger.Error("Failed to convert result to proto", zap.Error(err))
		return nil, status.Errorf(codes.Internal, "failed to convert result: %v", err)
	}

	return pbResult, nil
}

// convertProofConfig converts protobuf ProofConfig to prover.ProofConfig
func convertProofConfig(pbConfig *pb.ProofConfig) (*prover.ProofConfig, error) {
	if pbConfig == nil {
		// Use default configuration
		return &prover.ProofConfig{
			Timeout:       30 * time.Second,
			CPUTimeLimit:  10 * time.Second,
			MemoryLimit:   1024 * 1024 * 1024, // 1GB
			StackLimit:    8 * 1024 * 1024,    // 8MB
			FileSizeLimit: 100 * 1024 * 1024,  // 100MB
			NumFileLimit:  1024,
			AllTactics:    false,
			AST:           false,
			Tactics:       false,
			Premises:      false,
		}, nil
	}

	config := &prover.ProofConfig{
		AllTactics:    pbConfig.AllTactics,
		AST:           pbConfig.Ast,
		Tactics:       pbConfig.Tactics,
		Premises:      pbConfig.Premises,
		MemoryLimit:   pbConfig.MemoryLimit,
		StackLimit:    pbConfig.StackLimit,
		FileSizeLimit: pbConfig.FileSizeLimit,
		NumFileLimit:  pbConfig.NumFileLimit,
	}

	// Convert timeout
	if pbConfig.Timeout != nil {
		config.Timeout = pbConfig.Timeout.AsDuration()
	} else {
		config.Timeout = 30 * time.Second
	}

	// Convert CPU time limit
	if pbConfig.CpuTimeLimit != nil {
		config.CPUTimeLimit = pbConfig.CpuTimeLimit.AsDuration()
	} else {
		config.CPUTimeLimit = 10 * time.Second
	}

	return config, nil
}

// convertToProtoResult converts prover.ProofResult to pb.ProofResult
func convertToProtoResult(result *prover.ProofResult) (*pb.ProofResult, error) {
	if result == nil {
		return nil, fmt.Errorf("result cannot be nil")
	}

	// Convert result to protobuf Struct - handle different map types
	var resultMap map[string]any
	switch v := result.Result.(type) {
	case map[string]any:
		resultMap = v
	case map[string]string:
		// Convert map[string]string to map[string]any
		resultMap = make(map[string]any, len(v))
		for k, val := range v {
			resultMap[k] = val
		}
	default:
		return nil, fmt.Errorf("unsupported result type: %T, expected map[string]any or map[string]string", result.Result)
	}

	resultStruct, err := structpb.NewStruct(resultMap)
	if err != nil {
		return nil, fmt.Errorf("failed to convert result to struct: %w", err)
	}

	return &pb.ProofResult{
		ProofId:      result.ProofID,
		Success:      result.Success,
		Status:       string(result.Status),
		Result:       resultStruct,
		ErrorMessage: result.ErrorMessage,
	}, nil
}
