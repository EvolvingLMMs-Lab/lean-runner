// Package main is the entry point for the gRPC server.
package main

import (
	"flag"

	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/app"
)

var (
	port        = flag.Int("port", 50051, "The server port")
	host        = flag.String("host", "0.0.0.0", "The server host")
	logLevel    = flag.String("log-level", "", "The log level (debug, info, warn, error)")
	configFile  = flag.String("config", "", "Path to config file (default: use built-in defaults)")
	concurrency = flag.Int("concurrency", 0, "Lean concurrency (0 = use config default)")
)

func main() {
	flag.Parse()

	opts := &app.CliOptions{
		Port:        *port,
		Host:        *host,
		LogLevel:    *logLevel,
		ConfigFile:  *configFile,
		Concurrency: *concurrency,
	}

	app.Run(opts)
}
