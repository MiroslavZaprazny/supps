function set_service_name(tag, timestamp, record)
    local service_name = "other"

    local container_name = record["container_name"]
    if container_name then
        service_name = string.gsub(container_name, "^/", "")
    end

    record["service_name"] = service_name

    return 1, timestamp, record
end