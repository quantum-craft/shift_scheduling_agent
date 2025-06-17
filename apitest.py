import os
import asyncio
from dotenv import load_dotenv

from hrm.webapi.unified.employees import employees as emp_api
from hrm.webapi.unified.groups.customs import groups as customgroup_api
from hrm.webapi.unified.groups.customs import employees as customgroupemp_api
from hrm.webapi.unified.groups.customs.shift_schedule_sections import requieements as groupreq_api


if __name__ == "__main__":
    async def main():
        load_dotenv(dotenv_path=".env", override=True)
        token = os.getenv("DEFAULT_TOKEN")

        # print(f"employees.get_my_employee_info {await emp_api.get_my_employee_info(token)}")
        # print(f"groups.get_custom_group_info {await customgroup_api.get_custom_group_info(token)}")
        # print(f"groups.get_custom_group_info {await customgroupemp_api.get_employees_info(token)}")
        print(f"groupreq_api.get_requirements {await groupreq_api.get_requirements(token)}")

    asyncio.run(main())
