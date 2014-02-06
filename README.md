TimeReg
=======
TimeReg is a simple time registration system written in python using Django.

In TimeReg, registrations are associated with a project and/or project phase.
Hence projects can be single entities, but they can also consist of different
phases.

TimeReg allows users to export timesheets, containing their registrations, for
the projects they've been working on, aswell as users with administrator rights
to export timesheets for all users aswell as projects. TimeReg supports export
to PDF and CSV.


TimeReg can import ics files into projects [0].


Todo:
-----
* Responsiveness!
* Prettier printing of time sheets.
* Include option to show start and end times of registration.
* Make administrators capable of printing sheets with all registrations on a project and users.
* CSV export

[0]: Whole day events aren't supported.
