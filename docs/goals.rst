.. Design goals and implementation

Design Goals
============
An important design goal for ``lorax`` was to implement best practices for
service architecture, software engineering, deployment, and monitoring.  These
goals were challenging because the calculations behind ``lorax`` can be quite
computationally-intensive, with some calculations taking days or week to
complete.  As a result ``lorax`` was implemented as a software ecosystem with
many components:

* Front-end web proxy
* Middleware server/dispatcher
* Calculational queues running multiple binaries
* Queue dispatching and management
* Database and filesystem access
