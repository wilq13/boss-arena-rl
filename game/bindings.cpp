#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <stdexcept>
#include "World.h"

namespace py = pybind11;

PYBIND11_MODULE(boss_arena_core, m) {
    // Config: создается из Python, поля можно менять (curriculum).
    // World копирует Config в конструкторе: менять поля нужно ДО создания World.
    py::class_<Config>(m, "Config")
        .def(py::init<>())
        .def_readwrite("playerHP", &Config::playerHP)
        .def_readwrite("playerSpeed", &Config::playerSpeed)
        .def_readwrite("playerRadius", &Config::playerRadius)
        .def_readwrite("fireCooldown", &Config::fireCooldown)
        .def_readwrite("switchSteps", &Config::switchSteps)
        .def_readwrite("dt", &Config::dt)
        .def_readwrite("bulletPower", &Config::bulletPower)
        .def_readwrite("bulletSpeed", &Config::bulletSpeed)
        .def_readwrite("shieldBlock", &Config::shieldBlock)
        .def_readwrite("bossHP", &Config::bossHP)
        .def_readwrite("bossShotFreq", &Config::bossShotFreq)
        .def_readwrite("bossShotSpeed", &Config::bossShotSpeed)
        .def_readwrite("bossShotRadius", &Config::bossShotRadius)
        .def_readwrite("bossShotPower", &Config::bossShotPower)
        .def_readwrite("bossTentacleFreq", &Config::bossTentacleFreq)
        .def_readwrite("bossTentaclePower", &Config::bossTentaclePower)
        .def_readwrite("bossTentacleWarning", &Config::bossTentacleWarning)
        .def_readwrite("bossTentacleDuration", &Config::bossTentacleDuration)
        .def_readwrite("bossTentacleCols", &Config::bossTentacleCols)
        .def_readwrite("maxSteps", &Config::maxSteps)
        .def_readwrite("darkSquaresProportion", &Config::darkSquaresProportion)
        .def_readwrite("darkSquaresPower", &Config::darkSquaresPower)
        ;

    // StepResult: только чтение
    py::class_<StepResult>(m, "StepResult")
        .def_readonly("dmgToBoss", &StepResult::dmgToBoss)
        .def_readonly("dmgTaken", &StepResult::dmgTaken)
        .def_readonly("dmgFromGoo", &StepResult::dmgFromGoo)
        .def_readonly("dmgFromTentacle", &StepResult::dmgFromTentacle)
        .def_readonly("dmgFromDark", &StepResult::dmgFromDark)
        .def_readonly("bossKilled", &StepResult::bossKilled)
        .def_readonly("playerDead", &StepResult::playerDead)
        .def_readonly("truncated", &StepResult::truncated)
        ;

    py::class_<World>(m, "World")
        .def(py::init<const Config&>())
        .def("reset", &World::reset)
        .def("step", [](World& w, int move, int aim, bool shield, bool fire) {
            // из Python может прийти что угодно, а DIRS[move] за пределами массива — UB
            if (move < 0 || move > 8) throw std::out_of_range("move должен быть 0..8");
            if (aim < 0 || aim > 15) throw std::out_of_range("aim должен быть 0..15");
            return w.step(Action{move, aim, shield, fire});
        })
        .def("observe", [](const World& w) {
            py::array_t<float> obs(World::OBS_SIZE);
            w.getObservation(obs.mutable_data());
            return obs;
        })
        .def("step_count", &World::stepCount)
        .def_property_readonly_static("OBS_SIZE", [](py::object) { return World::OBS_SIZE; });
}
