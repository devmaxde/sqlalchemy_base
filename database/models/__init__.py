from sqlalchemy import MetaData


class BotUser(Base):
    __tablename__ = "bot_user"
    user_name = Column(String(45), primary_key=True)
    admin = Column(Boolean, default=False)


def get_combined_metadata():
    combined_meta_data = MetaData()
    # TODO add Bases from all modules here
    for declarative_base in []:  # eg: for declarative_base in [UserBase, ServerBase...]:
        for (table_name, table) in declarative_base.metadata.tables.items():
            combined_meta_data._add_table(table_name, table.schema, table)
    return combined_meta_data
