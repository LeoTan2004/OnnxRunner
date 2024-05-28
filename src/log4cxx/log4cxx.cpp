//
// Created by leo on 5/28/24.
//

#include <utility>

#include "log.h"
#include "string"

using namespace log;

class Log4Cxx : public Logger {
private:
    std::string format;
public:
    explicit Log4Cxx(std::string format = "%t [%n] %l %m") : format(std::move(format)) {}
};
