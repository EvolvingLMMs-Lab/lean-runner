---

## Code Generation

To generate the Go gRPC code from the `.proto` files, you need to have `protoc`, `protoc-gen-go`, and `protoc-gen-go-grpc` installed.

Run the following command from the project's root directory to generate the files into the `packages/server/gen/go/` directory:

```bash
protoc --go_out=./packages/server/gen/go --go_opt=paths=source_relative \
       --go-grpc_out=./packages/server/gen/go --go-grpc_opt=paths=source_relative \
       ./proto/lean_runner/*.proto
```
