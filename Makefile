JAVAC=javac
RUNTIME_DIR=runtime
RUNTIME_LIB=Runtime.java
LIB_DIR=lib

all:
	$(JAVAC) $(RUNTIME_DIR)/$(RUNTIME_LIB) -d $(LIB_DIR)
	export CLASSPATH=${CLASSPATH}:$(LIB_DIR)