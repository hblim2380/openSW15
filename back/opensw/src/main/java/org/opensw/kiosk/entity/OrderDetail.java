package org.opensw.kiosk.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
@Table(name = "orderdetail")
public class OrderDetail {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;

    private int orderId;
    private int menuId;
    private int amount;
    private int price;
    private boolean addCheese;
    private boolean addTuna;
    private boolean addKimchi;
    private boolean napkin;
}
