from __future__ import absolute_import, annotations

import logging
import os
from datetime import datetime
from typing import List, Optional

from wenet.common.interface.component import ComponentInterface
from wenet.common.interface.client import RestClient, ApikeyClient
from wenet.common.interface.exceptions import AuthenticationException
from wenet.common.model.task.task import TaskPage, Task
from wenet.common.model.task.transaction import TaskTransaction, TaskTransactionPage


logger = logging.getLogger("wenet.common.interface.task_manager")


class TaskManagerInterface(ComponentInterface):

    COMPONENT_PATH = os.getenv("TASK_MANAGER_PATH", "/task_manager")

    def __init__(self, client: RestClient, instance: str = ComponentInterface.PRODUCTION_INSTANCE, base_headers: Optional[dict] = None) -> None:
        if isinstance(client, ApikeyClient):
            base_url = instance + self.COMPONENT_PATH
        else:
            raise AuthenticationException("task manager")

        super().__init__(client, base_url, base_headers)

    def get_tasks(self,
                  app_id: str,
                  requester_id: Optional[str] = None,
                  task_type_id: Optional[str] = None,
                  goal_name: Optional[str] = None,
                  goal_description: Optional[str] = None,
                  creation_from: Optional[datetime] = None,
                  creation_to: Optional[datetime] = None,
                  update_from: Optional[datetime] = None,
                  update_to: Optional[datetime] = None,
                  has_close_ts: Optional[bool] = None,
                  closed_from: Optional[datetime] = None,
                  closed_to: Optional[datetime] = None,
                  order: Optional[str] = None,
                  offset: int = 0,
                  limit: Optional[int] = 100,
                  headers: Optional[dict] = None
                  ) -> List[Task]:
        """
        Get the tasks specifying query parameters
        Args:
            app_id: an application identifier to be equals on the tasks to return
            requester_id: an user identifier to be equals on the tasks to return
            task_type_id: a task type identifier to be equals on the tasks to return
            goal_name: a goal name to be equals on the tasks to return
            goal_description: a goal description to be equals on the tasks to return
            creation_from: the minimum creation date time of the tasks to return
            creation_to: the maximum creation date time of the tasks to return
            update_from: the minimum update date time of the tasks to return
            update_to: the maximum update date time of the tasks to return
            has_close_ts: get the closed or open tasks
            closed_from: the minimum close date time of the task
            closed_to: the maximum close date time of the task
            order: the order in witch the tasks have to be returned. For each field it has be separated by a ',' and each field can start with '+' (or without it) to order on ascending order, or with the prefix '-' to do on descendant order
            offset: The index of the first task to return. Default value is set to 0
            limit: the number maximum of tasks to return. Default value is set to 100. If set to None it will return all the tasks
            headers: additional headers

        Returns:
            the list of tasks
        """
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        query_params_temp = {
            "appId": app_id,
            "requesterId": requester_id,
            "taskTypeId": task_type_id,
            "goalName": goal_name,
            "goalDescription": goal_description,
            "creationFrom": int(creation_from.timestamp()) if creation_from is not None else None,
            "creationTo": int(creation_to.timestamp()) if creation_to is not None else None,
            "updateFrom": int(update_from.timestamp()) if update_from is not None else None,
            "updateTo": int(update_to.timestamp()) if update_to is not None else None,
            "hasCloseTs": has_close_ts,
            "closeFrom": int(closed_from.timestamp()) if closed_from is not None else None,
            "closeTo": int(closed_to.timestamp()) if closed_to is not None else None,
            "order": order,
            "offset": offset,
            "limit": limit
        }

        query_params = {}

        for key in query_params_temp:
            if query_params_temp[key] is not None:
                query_params[key] = query_params_temp[key]

        if limit is not None:
            response = self._client.get(f"{self._base_url}/tasks", query_params=query_params, headers=headers)

            if response.status_code == 200:
                task_page = TaskPage.from_repr(response.json())
                return task_page.tasks
            else:
                raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

        tasks = []
        query_params["limit"] = 100
        has_got_all_tasks = False
        while not has_got_all_tasks:
            response = self._client.get(f"{self._base_url}/tasks", query_params=query_params, headers=headers)

            if response.status_code == 200:
                task_page = TaskPage.from_repr(response.json())
            else:
                raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

            tasks.extend(task_page.tasks)
            query_params["offset"] += len(task_page.tasks)
            if len(task_page.tasks) < query_params["limit"]:
                has_got_all_tasks = True

        return tasks

    def get_transactions(self,
                         app_id: str,
                         requester_id: Optional[str] = None,
                         task_type_id: Optional[str] = None,
                         goal_name: Optional[str] = None,
                         goal_description: Optional[str] = None,
                         goal_keywords: Optional[str] = None,
                         task_creation_from: Optional[datetime] = None,
                         task_creation_to: Optional[datetime] = None,
                         task_update_from: Optional[datetime] = None,
                         task_update_to: Optional[datetime] = None,
                         has_close_ts: Optional[bool] = None,
                         closed_from: Optional[datetime] = None,
                         closed_to: Optional[datetime] = None,
                         task_id: Optional[str] = None,
                         transaction_id: Optional[str] = None,
                         transaction_label: Optional[str] = None,
                         actioneer_id: Optional[str] = None,
                         creation_from: Optional[datetime] = None,
                         creation_to: Optional[datetime] = None,
                         update_from: Optional[datetime] = None,
                         update_to: Optional[datetime] = None,
                         order: Optional[str] = None,
                         offset: int = 0,
                         limit: Optional[int] = 100,
                         headers: Optional[dict] = None
                         ) -> List[TaskTransaction]:
        """
        Get the transactions specifying query parameters
        Args:
            app_id: an application identifier to be equals on the tasks to return
            requester_id: an user identifier to be equals on the tasks to return
            task_type_id: a task type identifier to be equals on the tasks to return
            goal_name: a goal name to be equals on the tasks to return
            goal_description: a goal description to be equals on the tasks to return
            goal_keywords: a set of keywords to be defined on the task where are the transactions to return
            task_creation_from: the minimum creation date time of the task where are the transaction to return
            task_creation_to: the maximum creation date time of the task where are the transaction to return
            task_update_from: the minimum update date time of the task where are the transaction to return
            task_update_to: the maximum update date time of the task where are the transaction to return
            has_close_ts: get the closed or open tasks
            closed_from: the minimum close date time of the task
            closed_to: the maximum close date time of the task
            task_id: a task identifier to be equals on the task where are the transactions to return
            transaction_id: an identifier to be equals on the transactions to return
            transaction_label: a label to be equals on the transactions to return
            actioneer_id: an user identifier that has done the transactions to return
            creation_from: the minimum creation date time of the transactions to return
            creation_to: the maximum creation date time of the transactions to return
            update_from: the minimum update date time of the transactions to return
            update_to: the maximum update date time of the transactions to return
            order: the order in witch the tasks have to be returned. For each field it has be separated by a ',' and each field can start with '+' (or without it) to order on ascending order, or with the prefix '-' to do on descendant order
            offset: The index of the first task to return. Default value is set to 0
            limit: the number maximum of tasks to return. Default value is set to 100. If set to None it will return all the tasks
            headers: additional headers

        Returns:
            the list of transactions
        """
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        query_params_temp = {
            "appId": app_id,
            "requesterId": requester_id,
            "taskTypeId": task_type_id,
            "goalName": goal_name,
            "goalDescription": goal_description,
            "goalKeywords": goal_keywords,
            "taskCreationFrom": int(task_creation_from.timestamp()) if task_creation_from is not None else None,
            "taskCreationTo": int(task_creation_to.timestamp()) if task_creation_to is not None else None,
            "taskUpdateFrom": int(task_update_from.timestamp()) if task_update_from is not None else None,
            "taskUpdateTo": int(task_update_to.timestamp()) if task_update_to is not None else None,
            "hasCloseTs": has_close_ts,
            "closeFrom": int(closed_from.timestamp()) if closed_from is not None else None,
            "closeTo": int(closed_to.timestamp()) if closed_to is not None else None,
            "taskId": task_id,
            "id": transaction_id,
            "label": transaction_label,
            "actioneerId": actioneer_id,
            "creationFrom": int(creation_from.timestamp()) if creation_from is not None else None,
            "creationTo": int(creation_to.timestamp()) if creation_to is not None else None,
            "updateFrom": int(update_from.timestamp()) if update_from is not None else None,
            "updateTo": int(update_to.timestamp()) if update_to is not None else None,
            "order": order,
            "offset": offset,
            "limit": limit
        }

        query_params = {}

        for key in query_params_temp:
            if query_params_temp[key] is not None:
                query_params[key] = query_params_temp[key]

        if limit is not None:
            response = self._client.get(f"{self._base_url}/taskTransactions", query_params=query_params, headers=headers)

            if response.status_code == 200:
                transaction_page = TaskTransactionPage.from_repr(response.json())
                return transaction_page.transactions
            else:
                raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

        transactions = []
        has_got_all_transactions = False
        query_params["limit"] = 100
        while not has_got_all_transactions:
            response = self._client.get(f"{self._base_url}/taskTransactions", query_params=query_params, headers=headers)

            if response.status_code == 200:
                transaction_page = TaskTransactionPage.from_repr(response.json())
            else:
                raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

            transactions.extend(transaction_page.transactions)
            query_params["offset"] += len(transaction_page.transactions)
            if len(transaction_page.transactions) < query_params["limit"]:
                has_got_all_transactions = True

        return transactions

    def get_task(self, task_id: str, headers: Optional[dict] = None) -> Task:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        response = self._client.get(f"{self._base_url}/tasks/{task_id}", headers=headers)

        if response.status_code == 200:
            return Task.from_repr(response.json())
        else:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

    def get_task_page(self,
                      app_id: str,
                      requester_id: Optional[str] = None,
                      task_type_id: Optional[str] = None,
                      goal_name: Optional[str] = None,
                      goal_description: Optional[str] = None,
                      creation_from: Optional[datetime] = None,
                      creation_to: Optional[datetime] = None,
                      update_from: Optional[datetime] = None,
                      update_to: Optional[datetime] = None,
                      has_close_ts: Optional[bool] = None,
                      closed_from: Optional[datetime] = None,
                      closed_to: Optional[datetime] = None,
                      order: Optional[str] = None,
                      offset: int = 0,
                      limit: int = 100,
                      headers: Optional[dict] = None
                      ) -> TaskPage:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        query_params_temp = {
            "appId": app_id,
            "requesterId": requester_id,
            "taskTypeId": task_type_id,
            "goalName": goal_name,
            "goalDescription": goal_description,
            "creationFrom": int(creation_from.timestamp()) if creation_from is not None else None,
            "creationTo": int(creation_to.timestamp()) if creation_to is not None else None,
            "updateFrom": int(update_from.timestamp()) if update_from is not None else None,
            "updateTo": int(update_to.timestamp()) if update_to is not None else None,
            "hasCloseTs": has_close_ts,
            "closeFrom": int(closed_from.timestamp()) if closed_from is not None else None,
            "closeTo": int(closed_to.timestamp()) if closed_to is not None else None,
            "order": order,
            "offset": offset,
            "limit": limit
        }

        query_params = {}

        for key in query_params_temp:
            if query_params_temp[key] is not None:
                query_params[key] = query_params_temp[key]

        response = self._client.get(f"{self._base_url}/tasks", query_params=query_params, headers=headers)

        if response.status_code == 200:
            return TaskPage.from_repr(response.json())
        else:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

    def get_transaction_page(self,
                             app_id: str,
                             requester_id: Optional[str] = None,
                             task_type_id: Optional[str] = None,
                             goal_name: Optional[str] = None,
                             goal_description: Optional[str] = None,
                             goal_keywords: Optional[str] = None,
                             task_creation_from: Optional[datetime] = None,
                             task_creation_to: Optional[datetime] = None,
                             task_update_from: Optional[datetime] = None,
                             task_update_to: Optional[datetime] = None,
                             has_close_ts: Optional[bool] = None,
                             closed_from: Optional[datetime] = None,
                             closed_to: Optional[datetime] = None,
                             task_id: Optional[str] = None,
                             transaction_id: Optional[str] = None,
                             transaction_label: Optional[str] = None,
                             actioneer_id: Optional[str] = None,
                             creation_from: Optional[datetime] = None,
                             creation_to: Optional[datetime] = None,
                             update_from: Optional[datetime] = None,
                             update_to: Optional[datetime] = None,
                             order: Optional[str] = None,
                             offset: int = 0,
                             limit: int = 100,
                             headers: Optional[dict] = None
                             ) -> TaskTransactionPage:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        query_params_temp = {
            "appId": app_id,
            "requesterId": requester_id,
            "taskTypeId": task_type_id,
            "goalName": goal_name,
            "goalDescription": goal_description,
            "goalKeywords": goal_keywords,
            "taskCreationFrom": int(task_creation_from.timestamp()) if task_creation_from is not None else None,
            "taskCreationTo": int(task_creation_to.timestamp()) if task_creation_to is not None else None,
            "taskUpdateFrom": int(task_update_from.timestamp()) if task_update_from is not None else None,
            "taskUpdateTo": int(task_update_to.timestamp()) if task_update_to is not None else None,
            "hasCloseTs": has_close_ts,
            "closeFrom": int(closed_from.timestamp()) if closed_from is not None else None,
            "closeTo": int(closed_to.timestamp()) if closed_to is not None else None,
            "taskId": task_id,
            "id": transaction_id,
            "label": transaction_label,
            "actioneerId": actioneer_id,
            "creationFrom": int(creation_from.timestamp()) if creation_from is not None else None,
            "creationTo": int(creation_to.timestamp()) if creation_to is not None else None,
            "updateFrom": int(update_from.timestamp()) if update_from is not None else None,
            "updateTo": int(update_to.timestamp()) if update_to is not None else None,
            "order": order,
            "offset": offset,
            "limit": limit
        }

        query_params = {}

        for key in query_params_temp:
            if query_params_temp[key] is not None:
                query_params[key] = query_params_temp[key]

        response = self._client.get(f"{self._base_url}/taskTransactions", query_params=query_params, headers=headers)

        if response.status_code == 200:
            return TaskTransactionPage.from_repr(response.json())
        else:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

    def create_task(self, task: Task, headers: Optional[dict] = None) -> None:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        task_repr = task.prepare_task()
        task_repr.pop("id", None)
        response = self._client.post(f"{self._base_url}/tasks", body=task_repr, headers=headers)

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

    def update_task(self, task: Task, headers: Optional[dict] = None) -> None:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        response = self._client.put(f"{self._base_url}/tasks/{task.task_id}", body=task.prepare_task(), headers=headers)

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")

    def create_task_transaction(self, task_transaction: TaskTransaction, headers: Optional[dict] = None) -> None:
        if headers is not None:
            headers.update(self._base_headers)
        else:
            headers = self._base_headers

        response = self._client.post(f"{self._base_url}/tasks/transactions", body=task_transaction.to_repr(), headers=headers)

        if response.status_code not in [200, 201, 202]:
            raise Exception(f"Request has return a code [{response.status_code}] with content [{response.text}]")
