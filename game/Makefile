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
	rm -f *.o boss_arena test_world bench

.PHONY: all run test benchmark clean
