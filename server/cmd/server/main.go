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
	port     = flag.Int("port", 50051, "The server port")
	logLevel = flag.String("log-level", "info", "The log level") // debug, info, warn, error
)

func main() {
	flag.Parse()

	// Initialize the logger with command line log level
	config := logger.DefaultConfig()
	if *logLevel != "" {
		config.Level = logger.LogLevel(*logLevel)
	}
	if err := logger.Initialize(config); err != nil {
		// Fallback to basic logging if logger initialization fails
		fmt.Printf("Failed to initialize logger: %v\n", err)
		fmt.Printf("Using fallback logging configuration...\n")

		// Try to initialize with default config as fallback
		if fallbackErr := logger.Initialize(logger.DefaultConfig()); fallbackErr != nil {
			fmt.Printf("Failed to initialize fallback logger: %v\n", fallbackErr)
			fmt.Printf("Exiting due to logger initialization failure\n")
			return
		}
		fmt.Printf("Fallback logger initialized successfully\n")
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

	// proveService := service.NewProveService(...)
	// pb.RegisterProveServiceServer(s, proveService)

	logger.Info("Server listening", zap.String("address", lis.Addr().String()))

	// Start serving requests.
	if err := s.Serve(lis); err != nil {
		logger.Fatal("Failed to serve", zap.Error(err))
	}
}
