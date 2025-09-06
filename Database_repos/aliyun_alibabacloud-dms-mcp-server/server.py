import os
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from pydantic import BaseModel
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dms_enterprise20181101.client import Client as DmsEnterpriseClient
from alibabacloud_dms_enterprise20181101 import models as dms_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyBaseModel(BaseModel):
    model_config = {
        "json_encoders": {
            "str": lambda v: v.encode('utf-8').decode('utf-8') if isinstance(v, str) else v
        }
    }

class InstanceInfo(MyBaseModel):
    instance_id: Any
    host: Any
    port: Any

class DatabaseInfo(MyBaseModel):
    DatabaseId: Any
    DbType: Any
    Host: Any
    Port: Any
    SchemaName: Any

class InstanceDetail(MyBaseModel):
    InstanceId: Any
    InstanceAlias: Any
    InstanceType: Any
    State: Any

class DatabaseDetail(MyBaseModel):
    DatabaseId: Any
    InstanceId: Any
    InstanceAlias: Any
    DbType: Any
    SchemaName: Any
    State: Any

class Column(MyBaseModel):
    ColumnName: Any
    ColumnType: Any
    AutoIncrement: Any
    Description: Any
    Nullable: Any

class Index(MyBaseModel):
    IndexName: Any
    IndexType: Any
    IndexColumns: Any
    Unique: Any

class TableDetail(MyBaseModel):
    ColumnList: Any
    IndexList: Any

class ResultSet(MyBaseModel):
    ColumnNames: List[str]
    Rows: List[Dict[str, Any]]
    RowCount: int
    Success: bool
    MarkdownTable: Optional[str] = None

class ExecuteScriptResult(MyBaseModel):
    RequestId: str
    Results: List[ResultSet]
    Success: bool

    def __str__(self) -> str:
        if not self.Results:
            return "No results returned"
        
        for result in self.Results:
            if result.MarkdownTable:
                return result.MarkdownTable
            elif result.Rows:
                return _format_as_markdown_table(result.ColumnNames, result.Rows)
        
        return f"Execution completed. Success: {self.Success}, RequestId: {self.RequestId}"

class SqlResult(MyBaseModel):
    sql: Optional[str] = None

class AskDatabaseResult(MyBaseModel):
    executed_sql: str
    execution_result: str

def _format_as_markdown_table(column_names, rows) -> str:
    if not rows or not column_names:
        return "No data available"
    
    header = "| " + " | ".join(str(col) for col in column_names) + " |"
    separator = "| " + " | ".join(["---"] * len(column_names)) + " |"
    
    table_rows = []
    for row in rows:
        table_row = "| " + " | ".join(str(row.get(col, "")) for col in column_names) + " |"
        table_rows.append(table_row)
    
    return "\n".join([header, separator] + table_rows)

def create_client() -> DmsEnterpriseClient:
    config = open_api_models.Config(
        access_key_id=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        security_token=os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN'),
        endpoint='dms-enterprise.aliyuncs.com',
        region_id=os.getenv('ALIBABA_CLOUD_REGION_ID', 'cn-hangzhou')
    )
    return DmsEnterpriseClient(config)

def add_instance(db_user, db_password, instance_resource_id, host, port, region) -> InstanceInfo:
    client = create_client()
    request = dms_models.RegisterInstanceRequest(
        instance_source='OTHER',
        instance_type='MySQL',
        network_type='VPC',
        env_type='test',
        host=host,
        port=int(port),
        sid='',
        database_user=db_user,
        database_password=db_password,
        instance_alias=f'{host}:{port}',
        dba_id='',
        safe_rule='free',
        query_timeout=30,
        export_timeout=600,
        ecs_region=region,
        vpc_id='',
        instance_id=instance_resource_id
    )
    runtime = util_models.RuntimeOptions()
    response = client.register_instance_with_options(request, runtime)
    return InstanceInfo(
        instance_id=response.instance_id,
        host=host,
        port=port
    )

def get_instance(host, port, sid) -> InstanceDetail:
    client = create_client()
    request = dms_models.GetInstanceRequest(
        host=host,
        port=int(port),
        sid=sid
    )
    runtime = util_models.RuntimeOptions()
    response = client.get_instance_with_options(request, runtime)
    return InstanceDetail(
        InstanceId=response.instance.instance_id,
        InstanceAlias=response.instance.instance_alias,
        InstanceType=response.instance.instance_type,
        State=response.instance.state
    )

def search_database(search_key, page_number, page_size) -> List[DatabaseInfo]:
    client = create_client()
    request = dms_models.SearchDatabaseRequest(
        search_key=search_key,
        page_number=int(page_number),
        page_size=int(page_size)
    )
    runtime = util_models.RuntimeOptions()
    response = client.search_database_with_options(request, runtime)
    
    databases = []
    for db in response.search_database_list:
        databases.append(DatabaseInfo(
            DatabaseId=db.database_id,
            DbType=db.db_type,
            Host=db.host,
            Port=db.port,
            SchemaName=db.schema_name
        ))
    return databases

def get_database(host, port, schema_name, sid) -> DatabaseDetail:
    client = create_client()
    request = dms_models.GetDatabaseRequest(
        host=host,
        port=int(port),
        schema_name=schema_name,
        sid=sid
    )
    runtime = util_models.RuntimeOptions()
    response = client.get_database_with_options(request, runtime)
    return DatabaseDetail(
        DatabaseId=response.database.database_id,
        InstanceId=response.database.instance_id,
        InstanceAlias=response.database.instance_alias,
        DbType=response.database.db_type,
        SchemaName=response.database.schema_name,
        State=response.database.state
    )

def list_tables(database_id, search_name, page_number, page_size) -> Dict[str, Any]:
    client = create_client()
    request = dms_models.ListTablesRequest(
        database_id=database_id,
        search_name=search_name,
        page_number=int(page_number),
        page_size=int(page_size)
    )
    runtime = util_models.RuntimeOptions()
    response = client.list_tables_with_options(request, runtime)
    return {
        'tables': response.table_list,
        'total_count': response.total_count
    }

def get_meta_table_detail_info(table_guid) -> TableDetail:
    client = create_client()
    request = dms_models.GetMetaTableDetailInfoRequest(
        table_guid=table_guid
    )
    runtime = util_models.RuntimeOptions()
    response = client.get_meta_table_detail_info_with_options(request, runtime)
    
    columns = []
    for col in response.column_list:
        columns.append(Column(
            ColumnName=col.column_name,
            ColumnType=col.column_type,
            AutoIncrement=col.auto_increment,
            Description=col.description,
            Nullable=col.nullable
        ))
    
    indexes = []
    for idx in response.index_list:
        indexes.append(Index(
            IndexName=idx.index_name,
            IndexType=idx.index_type,
            IndexColumns=idx.index_columns,
            Unique=idx.unique
        ))
    
    return TableDetail(
        ColumnList=columns,
        IndexList=indexes
    )

def execute_script(database_id, script, logic) -> ExecuteScriptResult:
    client = create_client()
    request = dms_models.ExecuteScriptRequest(
        db_id=database_id,
        script=script,
        logic=bool(logic)
    )
    runtime = util_models.RuntimeOptions()
    response = client.execute_script_with_options(request, runtime)
    
    results = []
    for result in response.results:
        column_names = result.column_names if hasattr(result, 'column_names') else []
        rows = result.rows if hasattr(result, 'rows') else []
        
        result_set = ResultSet(
            ColumnNames=column_names,
            Rows=rows,
            RowCount=len(rows),
            Success=result.success if hasattr(result, 'success') else True,
            MarkdownTable=_format_as_markdown_table(column_names, rows) if rows else None
        )
        results.append(result_set)
    
    return ExecuteScriptResult(
        RequestId=response.request_id,
        Results=results,
        Success=response.success
    )

def nl2sql(database_id, question, knowledge) -> SqlResult:
    client = create_client()
    request = dms_models.NL2SQLRequest(
        db_id=database_id,
        question=question,
        knowledge=knowledge
    )
    runtime = util_models.RuntimeOptions()
    response = client.nl2sql_with_options(request, runtime)
    return SqlResult(sql=response.sql)

class ToolRegistry:
    def __init__(self, mcp):
        self.mcp = mcp
        self.default_database_id = getattr(mcp.state, 'default_database_id', None) if hasattr(mcp, 'state') else None
    
    def _register_configured_db_toolset(self) -> None:
        self.mcp.tool()(list_tables)
        self.mcp.tool()(get_meta_table_detail_info)
        self.mcp.tool()(execute_script)
        self.mcp.tool()(nl2sql)
    
    def _register_full_toolset(self) -> None:
        self.mcp.tool()(add_instance)
        self.mcp.tool()(get_instance)
        self.mcp.tool()(search_database)
        self.mcp.tool()(get_database)
        self.mcp.tool()(list_tables)
        self.mcp.tool()(get_meta_table_detail_info)
        self.mcp.tool()(execute_script)
        self.mcp.tool()(nl2sql)
    
    def register_tools(self) -> FastMCP:
        if self.default_database_id:
            self._register_configured_db_toolset()
        else:
            self._register_full_toolset()
        return self.mcp

async def lifespan(app) -> AsyncGenerator[None, None]:
    yield

def run_server() -> None:
    mcp = FastMCP(
        "alibabacloud-dms-mcp-server",
        dependencies=["alibabacloud_tea_openapi", "alibabacloud_dms_enterprise20181101"],
        lifespan=lifespan
    )
    
    tool_registry = ToolRegistry(mcp)
    tool_registry.register_tools()
    
    mcp.run(transport='stdio')

def main() -> None:
    run_server()

if __name__ == "__main__":
    main()