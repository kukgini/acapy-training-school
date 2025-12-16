use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::SystemTime;

use indy_vdr::common::error::prelude::*;
use indy_vdr::pool::{LocalPool, PoolTransactions};

pub const INDY_NETWORKS_GITHUB: &str = "https://github.com/IDunion/indy-did-networks";
pub const GENESIS_FILENAME: &str = "pool_transactions_genesis.json";

pub struct PoolState {
    pub pool: Option<LocalPool>,
    pub last_refresh: Option<SystemTime>,
    pub transactions: PoolTransactions,
}

pub struct AppState {
    pub is_multiple: bool,
    pub pool_states: HashMap<String, PoolState>,
}

pub fn init_pool_state_from_folder_structure(
    path: PathBuf,
) -> VdrResult<HashMap<String, PoolState>> {
    let mut networks = HashMap::new();

    let entries = fs::read_dir(path).map_err(|err| {
        err_msg(
            VdrErrorKind::FileSystem,
            "Could not read local networks folder",
        )
        .with_source(err)
    })?;

    for entry in entries {
        let entry = entry.map_err(|err| {
            err_msg(VdrErrorKind::FileSystem, "Could not read directory entry").with_source(err)
        })?;

        let file_name = entry.file_name();
        let file_name_str = file_name.to_str().ok_or_else(|| {
            err_msg(VdrErrorKind::FileSystem, "Invalid UTF-8 in directory name")
        })?;

        // filter hidden directories starting with "." and files
        let metadata = entry.metadata().map_err(|err| {
            err_msg(VdrErrorKind::FileSystem, "Could not read entry metadata").with_source(err)
        })?;

        if file_name_str.starts_with('.') || !metadata.is_dir() {
            continue;
        }

        let namespace = entry
            .path()
            .file_name()
            .ok_or_else(|| err_msg(VdrErrorKind::FileSystem, "Could not get directory name"))?
            .to_owned();

        let namespace_str = namespace.to_str().ok_or_else(|| {
            err_msg(VdrErrorKind::FileSystem, "Invalid UTF-8 in namespace")
        })?;

        let sub_entries = fs::read_dir(entry.path()).map_err(|err| {
            err_msg(
                VdrErrorKind::FileSystem,
                format!("Could not read subdirectory: {}", namespace_str),
            )
            .with_source(err)
        })?;

        for sub_entry in sub_entries {
            let sub_entry = sub_entry.map_err(|err| {
                err_msg(VdrErrorKind::FileSystem, "Could not read sub-entry").with_source(err)
            })?;
            let sub_entry_path = sub_entry.path();
            let sub_namespace = if sub_entry_path.is_dir() {
                sub_entry_path.file_name()
            } else {
                None
            };
            let (ledger_prefix, genesis_txns) = match sub_namespace {
                Some(sub_namespace) => {
                    let sub_namespace_str = sub_namespace.to_str().ok_or_else(|| {
                        err_msg(VdrErrorKind::FileSystem, "Invalid UTF-8 in sub-namespace")
                    })?;
                    (
                        format!("{}:{}", namespace_str, sub_namespace_str),
                        PoolTransactions::from_json_file(sub_entry_path.join(GENESIS_FILENAME))?,
                    )
                }
                None => (
                    String::from(namespace_str),
                    PoolTransactions::from_json_file(entry.path().join(GENESIS_FILENAME))?,
                ),
            };
            let pool_state = PoolState {
                pool: None,
                last_refresh: None,
                transactions: genesis_txns,
            };
            networks.insert(ledger_prefix, pool_state);
        }
    }
    Ok(networks)
}