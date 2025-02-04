from dateutil.parser import parse


def parse_uplink_gateway_info(things_uplink_message: dict, source: str):
    """Parses the desirable gateway information from a Things v3 JSON uplink message
    and returns comma-separated records for each gateway reached.
    """
    rec = things_uplink_message
    gtw_recs = []  # holds gateway records

    dev_id = rec["end_device_ids"]["device_id"]
    dev_eui = rec["end_device_ids"]["dev_eui"]
    ctr = rec["uplink_message"]["f_cnt"]              # frame counter
    ts = int(parse(rec["received_at"]).timestamp())
    dr = rec["uplink_message"]["settings"]["data_rate"]["lora"]
    data_rate = f"SF{dr['spreading_factor']}BW{int(dr['bandwidth'] / 1000)}"

    # add to list of gateway records
    for gtw in rec["uplink_message"]["rx_metadata"]:
        r = {}
        r["gtw_id"] = gtw["gateway_ids"]["gateway_id"]
        r["gtw_eui"] = gtw["gateway_ids"]["eui"]
        r["snr"] = gtw["snr"]
        r["rssi"] = gtw["rssi"]
        gtw_recs.append(r)

    final_recs = []
    for gtw in gtw_recs:
        r = f"{source},{ts},{dev_id},{dev_eui},{ctr},{gtw['gtw_id']},{gtw['gtw_eui']},{gtw['snr']},{gtw['rssi']},{data_rate}"
        final_recs.append(r)

    return final_recs

