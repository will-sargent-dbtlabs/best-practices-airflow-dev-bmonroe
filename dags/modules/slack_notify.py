from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.models.variable import Variable

SLACK_CONN_ID = "slack"
ENV = Variable.get("airflow-env")

def task_fail_slack_alert(context):
    """
    Callback task that can be used in DAG to alert of failure task completion

    Args:
        context (dict): Context variable passed in from Airflow

    Returns:
        None: Calls the SlackWebhookOperator execute method internally

    """
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed.
            *Env*: {env} 
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *Log Url*: {log_url} 
            """.format(
        env=ENV,
        task=context.get("task_instance").task_id,
        dag=context.get("task_instance").dag_id,
        ti=context.get("task_instance"),
        exec_date=context.get("execution_date"),
        log_url=context.get("task_instance").log_url,
    )

    failed_alert = SlackWebhookOperator(
        task_id="slack_notify",
        http_conn_id=SLACK_CONN_ID,
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username="airflow",
    )

    return failed_alert.execute(context=context)
