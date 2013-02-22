JAVAC=javac
RUNTIME_DIR=runtime
RUNTIME_LIB=Runtime.java
LIB_DIR=lib
TEST_DIR=tests

all:
	$(JAVAC) $(RUNTIME_DIR)/$(RUNTIME_LIB) -d $(LIB_DIR)

clean:
	rm $(LIB_DIR)/*.class

test:
	@CLASSPATH=$(LIB_DIR) $(TEST_DIR)/test.sh

test_clean:
	find -f $(TEST_DIR) -iname *.class -exec rm -f {} \
