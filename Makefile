CC=clang
RUNTIME_DIR=runtime
RUNTIME_SOURCE=runtime.c
LIB_DIR=lib
RUNTIME_LIB=runtime.bc
TEST_DIR=tests/lattests/

all:
	$(CC) -S -emit-llvm $(RUNTIME_DIR)/$(RUNTIME_SOURCE) -o $(LIB_DIR)/$(RUNTIME_LIB)

clean:
	rm -f $(LIB_DIR)/$(RUNTIME_LIB)

test_clean:
	find $(TEST_DIR) -type f -name "*.ll" -exec rm -f {} \;
	find $(TEST_DIR) -type f -name "*.bc" -exec rm -f {} \;
	find $(TEST_DIR) -type f -name "*.s" -exec rm -f {} \;
	find $(TEST_DIR) -type f -name "*.out" -exec rm -f {} \;
