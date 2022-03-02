#!/bin/bash

cowsay "Building Linux (amd64)..."
env GOOS=linux GOARCH=amd64 go build -o bin/linux/amd64/no-role-kick

cowsay "Building Windows (amd64)..."
env GOOS=windows GOARCH=amd64 go build -o bin/windows/amd64/no-role-kick.exe

cowsay "Building MacOS (amd64)..."
env GOOS=darwin GOARCH=amd64 go build -o bin/darwin/amd64/no-role-kick

cowsay "Build complete!"