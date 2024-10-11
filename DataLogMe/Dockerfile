FROM rust:latest

# Install dependencies and clone Cozo repository
RUN apt-get update && apt-get install -y git && \
    git clone https://github.com/cozodb/cozo.git && \
    cd cozo && cargo build --release

# Set the working directory
WORKDIR /cozo

# Command to run Cozo server
CMD ["./target/release/cozo", "serve"]
