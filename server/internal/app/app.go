// Package app contains the core application logic for the server.
package app

import (
	"fmt"
	"log"
	"net"

	pb "github.com/EvolvingLMMs-Lab/lean-runner/server/gen/go/proto"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/config"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/service"
	"go.uber.org/zap"
	"google.golang.org/grpc"
)

// CliOptions holds the command-line options passed to the application.
type CliOptions struct {
	Port        int
	Host        string
	LogLevel    string
	ConfigFile  string
	Concurrency int
}

// Run initializes and starts the gRPC server.
func Run(opts *CliOptions) {
	// Load configuration
	if err := config.LoadGlobalConfig(opts.ConfigFile); err != nil {
		// Use standard log for early errors before structured logger is available
		log.Printf("Failed to load configuration: %v", err)
		return
	}

	manager := config.GetGlobalManager()

	// Override config with command line flags (CLI flags have highest priority)
	if opts.Port != 50051 { // Default port changed
		manager.Set("server.port", opts.Port)
	}
	if opts.Host != "localhost" { // Default host changed
		manager.Set("server.host", opts.Host)
	}
	if opts.LogLevel != "" {
		manager.Set("logger.level", opts.LogLevel)
	}
	if opts.Concurrency > 0 {
		manager.Set("lean.concurrency", opts.Concurrency)
	}

	// Get the final config (values have been updated by Set calls)
	cfg := config.GetGlobalConfig()

	// Initialize logger with config
	loggerConfig := &logger.Config{
		Level:      logger.LogLevel(cfg.Logger.Level),
		Production: cfg.Logger.Production,
		OutputPath: cfg.Logger.OutputPath,
	}
	if err := logger.Initialize(loggerConfig); err != nil {
		// Fallback to basic logging if logger initialization fails
		log.Printf("Failed to initialize logger: %v", err)
		log.Printf("Using fallback logging configuration...")

		// Try to initialize with default config as fallback
		if fallbackErr := logger.Initialize(logger.DefaultConfig()); fallbackErr != nil {
			log.Printf("Failed to initialize fallback logger: %v", fallbackErr)
			log.Printf("Exiting due to logger initialization failure")
			return
		}
		log.Printf("Fallback logger initialized successfully")
	}
	defer logger.Sync() // Flush any buffered log entries

	logger.Info("Starting gRPC server",
		zap.String("host", cfg.Server.Host),
		zap.Int("port", cfg.Server.Port),
		zap.String("config_file", manager.GetConfigFile()))

	// Create a TCP listener on the specified host and port.
	address := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	lis, err := net.Listen("tcp", address)
	if err != nil {
		logger.Fatal("Failed to listen", zap.Error(err), zap.String("address", address))
	}

	// Create a new gRPC server.
	s := grpc.NewServer()

	// --- Register gRPC Services ---
	// Register the UtilsService.
	utilsService := service.NewUtilsService()
	pb.RegisterUtilsServiceServer(s, utilsService)

	// Register the ProverService.
	proverService := service.NewProverService(cfg)
	pb.RegisterProveServiceServer(s, proverService)

	logger.Info("Server listening", zap.String("address", lis.Addr().String()))

	// Start serving requests.
	if err := s.Serve(lis); err != nil {
		logger.Fatal("Failed to serve", zap.Error(err))
	}
}
