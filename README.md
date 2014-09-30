TimeReg
=======
TimeReg is a simple time registration system written in python using Django.
It's undone work, in a somewhat alpha-kinda working stage.

In TimeReg, registrations are associated with a project and/or project phase.
Hence projects can be single entities, but they can also consist of different
phases.

TimeReg allows users to export timesheets, containing their registrations, for
the projects they've been working on, ~~aswell as users with administrator rights
to export timesheets for all users aswell as projects. TimeReg supports export
to PDF and CSV.~~


TimeReg can import ics files into projects [0].


Todo:
-----
* Prettier printing of time sheets.
* Include option to show start and end times of registration in export to PDF.
* Make administrators capable of printing sheets with all registrations on a project and users.

[0]: all-day events aren't supported.
