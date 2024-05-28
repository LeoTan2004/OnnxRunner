//
// Created by leo on 5/28/24.
//

#ifndef DRONE_LOG_H
#define DRONE_LOG_H
namespace log {
    class Logger {

    public:
        virtual void debug(const char *message) = 0;

        virtual void info(const char *message) = 0;

        virtual void tracert(const char *message) = 0;

        virtual void error(const char *message) = 0;

        virtual void fatal(const char *message) = 0;

        virtual void warn(const char *message) = 0;
    };
}


#endif //DRONE_LOG_H
