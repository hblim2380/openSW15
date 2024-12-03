package org.opensw.kiosk.entity;

import lombok.Data;
import lombok.ToString;

import java.util.List;

@Data
@ToString
public class OrderRequest {

    private List<OrderItemRequest> items;

    public int calculateTotalPrice() {
        return items.stream().mapToInt(OrderItemRequest::getTotalPrice).sum();
    }
}
