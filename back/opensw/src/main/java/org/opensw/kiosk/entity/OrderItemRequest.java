package org.opensw.kiosk.entity;

import lombok.Data;

import java.util.List;

@Data
public class OrderItemRequest {
    private int menuId;
    private int quantity;
    private int totalPrice;
    private List<String> toppings;
    private boolean napkin;
}
