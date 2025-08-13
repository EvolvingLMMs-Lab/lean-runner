// Package main is the entry point for the gRPC server.
package main

import (
	"flag"
	"fmt"
	"net"

	pb "github.com/EvolvingLMMs-Lab/lean-runner/server/gen/go/proto"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/service"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

func main() {
	flag.Parse()

	// Initialize the logger
	if err := logger.InitializeFromEnv(); err != nil {
		// Fallback to basic logging if logger initialization fails
		fmt.Printf("Failed to initialize logger: %v\n", err)
		return
	}
	defer logger.Sync() // Flush any buffered log entries

	logger.Info("Starting gRPC server", zap.Int("port", *port))

	// Create a TCP listener on the specified port.
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		logger.Fatal("Failed to listen", zap.Error(err), zap.Int("port", *port))
	}

	// Create a new gRPC server.
	s := grpc.NewServer()

	// --- Register gRPC Services ---
	// Register the UtilsService.
	utilsService := service.NewUtilsService()
	pb.RegisterUtilsServiceServer(s, utilsService)

	// NOTE: When you create other services (like a ProveService),
	// you will register them here as well. For example:
	//
	// proveService := service.NewProveService(...)
	// pb.RegisterProveServiceServer(s, proveService)

	logger.Info("Server listening", zap.String("address", lis.Addr().String()))

	// Start serving requests.
	if err := s.Serve(lis); err != nil {
		logger.Fatal("Failed to serve", zap.Error(err))
	}
}
