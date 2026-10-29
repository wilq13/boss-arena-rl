CXX      = clang++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra -isystem /opt/homebrew/include
LDFLAGS  = -L/opt/homebrew/lib -lsfml-graphics -lsfml-window -lsfml-system

all: boss_arena test_world bench

boss_arena: main.o World.o Renderer.o
	$(CXX) $^ -o $@ $(LDFLAGS)

# тест без SFML: World не должен от него зависеть
test_world: test_world.o World.o
	$(CXX) $^ -o $@

bench: bench.o World.o
	$(CXX) $^ -o $@

# Python-модуль: World без SFML, собирается в rl_agent/ под Python из .venv
PY     = ../rl_agent/.venv/bin/python
PYINC  = $(shell $(PY) -m pybind11 --includes)
EXT    = $(shell $(PY) -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
MODULE = ../rl_agent/boss_arena_core$(EXT)

module: $(MODULE)

$(MODULE): bindings.cpp World.cpp World.h Config.h
	$(CXX) -std=c++17 -O2 -Wall -Wextra -shared -fPIC -undefined dynamic_lookup $(PYINC) bindings.cpp World.cpp -o $@

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $<

main.o World.o Renderer.o test_world.o bench.o: World.h Config.h
main.o Renderer.o: Renderer.h

run: boss_arena
	./boss_arena

test: test_world
	./test_world

benchmark: bench
	./bench

clean:
	rm -f *.o boss_arena test_world bench $(MODULE)

.PHONY: all run test benchmark module clean
