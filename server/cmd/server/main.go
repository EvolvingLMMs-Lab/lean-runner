// Package main is the entry point for the gRPC server.
package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	pb "github.com/EvolvingLMMs-Lab/lean-runner/server/gen/go/proto"
	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/service"
	"google.golang.org/grpc"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

func main() {
	flag.Parse()

	// Create a TCP listener on the specified port.
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
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

	log.Printf("server listening at %v", lis.Addr())

	// Start serving requests.
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
