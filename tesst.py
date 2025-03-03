def extract_mappings(data):
    node_mapping = {}
    link_mapping = {}
    
    # Khởi tạo node_mapping và link_mapping
    for key in data.keys():
        if key.startswith('xNode_'):
            # Phân tách thông tin từ key
            _, sfc_id, config_id, v_node, phy_node = key.split('_')
            sfc_id = int(sfc_id)
            config_id = int(config_id)
            v_node = int(v_node)
            phy_node = int(phy_node)
            # Khởi tạo ánh xạ cho node
            if (sfc_id, config_id) not in node_mapping:
                node_mapping[(sfc_id, config_id)] = {}
            node_mapping[(sfc_id, config_id)][v_node] = phy_node
            
        elif key.startswith('xEdge_'):
            # Phân tách thông tin từ key
            a = key.split('_', 3)
            print(a)
            # sfc_id = int(sfc_id)
            # config_id = int(config_id)    
            # edge_data = edge_data.replace('(', '').replace(')', '')
            # print(edge_data)        
    
    return node_mapping, link_mapping

# Dữ liệu đầu vào
data = {
    'phi_1_1': 1.0, 'pi_1': 1.0,
    'xEdge_1_1_(0,_1)_(1,_4)': 1.0, 'xEdge_1_1_(0,_2)_(1,_5)': 1.0,
    'xEdge_1_1_(1,_3)_(4,_6)': 1.0, 'xEdge_1_1_(2,_3)_(5,_6)': 1.0,
    'xNode_1_1_0_1': 1.0, 'xNode_1_1_1_4': 1.0,
    'xNode_1_1_2_5': 1.0, 'xNode_1_1_3_6': 1.0,
    'z_1_1': 1.0
}

node_mapping, link_mapping = extract_mappings(data)

# print("Node Mapping:", node_mapping)
# print("Link Mapping:", link_mapping)
