// Package config provides centralized configuration management using Viper.
package config

import (
	"errors"
	"fmt"
	"strings"

	"github.com/EvolvingLMMs-Lab/lean-runner/server/internal/logger"
	"github.com/spf13/viper"
	"go.uber.org/zap"
)

// Manager handles configuration loading and management
type Manager struct {
	config *Config
	v      *viper.Viper
}

// NewManager creates a new configuration manager
func NewManager() *Manager {
	return &Manager{
		v: viper.New(),
	}
}

// LoadConfig loads configuration from files, environment variables, and command line flags
func (m *Manager) LoadConfig(configFile string) error {
	logger.Debug("Loading configuration", zap.String("config_file", configFile))
	// Set default values
	m.setDefaults()

	// Configure Viper
	m.v.SetConfigName("config")
	m.v.SetConfigType("yaml")
	m.v.AddConfigPath("./configs")
	m.v.AddConfigPath(".")

	// Enable environment variable support
	m.v.AutomaticEnv()
	m.v.SetEnvPrefix("LEAN_RUNNER")
	m.v.SetEnvKeyReplacer(strings.NewReplacer(".", "_", "-", "_"))

	// If a custom config file is specified, load and merge it
	if configFile != "" && configFile != "default" {
		logger.Debug("Loading custom configuration file", zap.String("file", configFile))
		if err := m.loadCustomConfig(configFile); err != nil {
			return fmt.Errorf("failed to load custom config from %s: %w", configFile, err)
		}
	}

	// Unmarshal configuration into struct
	if err := m.v.Unmarshal(&m.config); err != nil {
		return fmt.Errorf("failed to unmarshal config: %w", err)
	}

	// Validate configuration
	if err := m.validateConfig(); err != nil {
		return fmt.Errorf("config validation failed: %w", err)
	}

	logger.Info("Configuration loaded successfully",
		zap.String("source", m.GetConfigFile()),
		zap.String("server_host", m.config.Server.Host),
		zap.Int("server_port", m.config.Server.Port),
		zap.String("log_level", m.config.Logger.Level),
		zap.Int("lean_concurrency", m.config.Lean.Concurrency))

	return nil
}

// setDefaults sets default configuration values
func (m *Manager) setDefaults() {
	// Server defaults
	m.v.SetDefault("server.host", "localhost")
	m.v.SetDefault("server.port", 50051)

	// Lean defaults
	m.v.SetDefault("lean.executable", "/root/.elan/bin/lake")
	m.v.SetDefault("lean.workspace", "/app/lean-runner/playground")
	m.v.SetDefault("lean.concurrency", 4)

	// Logger defaults
	m.v.SetDefault("logger.level", "info")
	m.v.SetDefault("logger.production", false)
	m.v.SetDefault("logger.output_path", "stdout")
}



// loadCustomConfig loads and merges a custom configuration file
func (m *Manager) loadCustomConfig(configFile string) error {
	// Create a new viper instance for the custom config
	customViper := viper.New()

	// Set the config file
	customViper.SetConfigFile(configFile)

	// Read the custom config
	if err := customViper.ReadInConfig(); err != nil {
		return err
	}

	// Merge the custom config with the current config
	if err := m.v.MergeConfigMap(customViper.AllSettings()); err != nil {
		return err
	}

	return nil
}

// validateConfig validates the loaded configuration
func (m *Manager) validateConfig() error {
	if m.config.Server.Port <= 0 || m.config.Server.Port > 65535 {
		return errors.New("server.port must be between 1 and 65535")
	}

	if m.config.Lean.Concurrency <= 0 {
		return errors.New("lean.concurrency must be greater than 0")
	}

	validLogLevels := map[string]bool{
		"debug": true, "info": true, "warn": true, "error": true,
	}
	if !validLogLevels[m.config.Logger.Level] {
		return fmt.Errorf("logger.level must be one of: debug, info, warn, error")
	}

	return nil
}

// GetConfig returns the loaded configuration
func (m *Manager) GetConfig() *Config {
	return m.config
}

// Set allows setting configuration values programmatically (useful for CLI flags)
func (m *Manager) Set(key string, value interface{}) {
	m.v.Set(key, value)
	// Re-unmarshal to update the config struct
	if err := m.v.Unmarshal(&m.config); err != nil {
		logger.Warn("Failed to unmarshal config after setting key",
			zap.String("key", key), zap.Error(err))
	}
}

// GetString returns a string configuration value
func (m *Manager) GetString(key string) string {
	return m.v.GetString(key)
}

// GetInt returns an integer configuration value
func (m *Manager) GetInt(key string) int {
	return m.v.GetInt(key)
}

// GetBool returns a boolean configuration value
func (m *Manager) GetBool(key string) bool {
	return m.v.GetBool(key)
}

// SaveConfig saves current configuration to a file
func (m *Manager) SaveConfig(filename string) error {
	if filename == "" {
		return m.v.WriteConfig()
	}
	return m.v.WriteConfigAs(filename)
}

// GetConfigFile returns the configuration file being used
func (m *Manager) GetConfigFile() string {
	configFile := m.v.ConfigFileUsed()
	if configFile == "" {
		return "defaults (embedded)"
	}
	return configFile
}

// Global configuration manager instance
var globalManager *Manager
var globalConfig *Config

// LoadGlobalConfig loads the global configuration
func LoadGlobalConfig(configFile string) error {
	globalManager = NewManager()
	if err := globalManager.LoadConfig(configFile); err != nil {
		return err
	}
	globalConfig = globalManager.GetConfig()
	return nil
}

// GetGlobalConfig returns the global configuration
func GetGlobalConfig() *Config {
	if globalConfig == nil {
		panic("Global configuration not loaded. Call LoadGlobalConfig first.")
	}
	return globalConfig
}

// GetGlobalManager returns the global configuration manager
func GetGlobalManager() *Manager {
	if globalManager == nil {
		panic("Global configuration manager not initialized. Call LoadGlobalConfig first.")
	}
	return globalManager
}

// SetGlobalConfigValue sets a value in the global configuration
func SetGlobalConfigValue(key string, value interface{}) {
	GetGlobalManager().Set(key, value)
}
