import os
import asyncio
from dotenv import load_dotenv

from uuid import UUID
from hrm.webapi.unified.employees import employees as emp_api
from hrm.webapi.unified.groups.customs import groups as customgroup_api
from hrm.webapi.unified.groups.customs import employees as customgroupemp_api
from hrm.webapi.unified.groups.customs.shift_schedule_sections import requieements as groupreq_api
from hrm.webapi.unified.shifts import shifts as shifts_api
from hrm.webapi.unified.shiftschedule import shiftschedule as shiftschedule_api
from hrm.webapi.unified.shiftschedule import cycles as shiftschedulecycles_api

if __name__ == "__main__":
    async def main():
        load_dotenv(dotenv_path=".env", override=True)
        token = os.getenv("DEFAULT_TOKEN")

        # print(f"employees.get_my_employee_info {await emp_api.get_my_employee_info(token)}")
        # print(f"groups.get_custom_group_info {await customgroup_api.get_custom_group_info(token)}")
        # print(f"groups.get_custom_group_info {await customgroupemp_api.get_employees_info(token)}")
        # print(f"groupreq_api.get_requirements {await groupreq_api.get_requirements(token)}")
        # print(f"shifts_api.get_shifts {await shifts_api.get_shifts(token,[ UUID('214ff328-eb67-4548-a298-1cc4665c810b')])}")
        print(f"shiftschedule_api.get_shiftschedules {await shiftschedule_api.get_shiftschedules(token,[ UUID('58244e12-47a3-4473-80cb-4e48daeb8c74')])}")
        # print(f"shiftschedulecycles_api.get_cycles {await shiftschedulecycles_api.get_cycles(token,[ UUID('58244e12-47a3-4473-80cb-4e48daeb8c74')])}")
    asyncio.run(main())
