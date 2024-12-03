package org.opensw.kiosk.repository;


import org.opensw.kiosk.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Integer> {
}
