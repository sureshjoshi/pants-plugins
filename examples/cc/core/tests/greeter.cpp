#include "core/greeter.h"
#include "catch.hpp"

TEST_CASE("Additions are correct", "[add]")
{
    REQUIRE(add(0, 0) == 0);
    REQUIRE(add(1, 2) == 2);
    REQUIRE(add(-1, -2) == -3);
}