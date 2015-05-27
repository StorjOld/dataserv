DROP TABLE IF EXISTS farmer_list;
CREATE TABLE farmer_list (
  id integer primary key autoincrement,
  btc_addr text not null,
  last_seen text,
  last_audit text
)