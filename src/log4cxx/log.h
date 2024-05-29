//
// Created by leo on 5/28/24.
//

#ifndef DRONE_LOG_H
#define DRONE_LOG_H

#include <string>

namespace log {
    enum LogLevel {
        TRACERT,
        DEBUG,
        INFO,
        WARNING,
        ERROR,
        FATAL
    };

    class Logger {

    public:
        virtual void tracert(std::string message) = 0;

        virtual void debug(std::string message) = 0;

        virtual void info(std::string message) = 0;

        virtual void warning(std::string message) = 0;

        virtual void error(std::string message) = 0;

        virtual void fatal(std::string message) = 0;

    };

    /**
     * LogHandler 是用来处理日志的，可以被多个Logger对象使用，一个Logger对象可以有多个LogHandler
     */
    class LogHandler {
        virtual LogLevel getLevel() = 0;

        virtual void handle(LogLevel level, std::string message) = 0;
    };

}


#endif //DRONE_LOG_H
