// Package service contains the implementations of the gRPC services.
package service

import (
	"context"

	pb "github.com/EvolvingLMMs-Lab/lean-runner/server/gen/go/proto"
	"google.golang.org/protobuf/types/known/emptypb"
)

// AppVersion is the version of the application.
// This can be set at build time using linker flags for production releases.
var AppVersion = "0.2.0-dev"

// UtilsService implements the gRPC UtilsService.
type UtilsService struct {
	// This embedding is required by gRPC for forward compatibility.
	pb.UnimplementedUtilsServiceServer
}

// NewUtilsService creates a new UtilsService.
func NewUtilsService() *UtilsService {
	return &UtilsService{}
}

// Health checks the health of the server and returns its status.
func (s *UtilsService) Health(ctx context.Context, _ *emptypb.Empty) (*pb.HealthResponse, error) {
	// In a real-world application, you might add checks here for database
	// connectivity or other dependencies.
	return &pb.HealthResponse{
		Status:  "SERVING",
		Message: "Server is up and running.",
		Version: AppVersion,
	}, nil
}
