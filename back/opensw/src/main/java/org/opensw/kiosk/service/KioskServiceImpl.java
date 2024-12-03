package org.opensw.kiosk.service;

import lombok.Builder;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.opensw.kiosk.entity.*;
import org.opensw.kiosk.repository.KioskRepository;
import org.opensw.kiosk.repository.OrderDetailRepository;
import org.opensw.kiosk.repository.OrderRepository;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
@Log4j2
public class KioskServiceImpl implements KioskService {

    private final KioskRepository kioskRepository;

    private final OrderRepository orderRepository;

    private final OrderDetailRepository orderDetailRepository;

    @Override
    public List<Menu> getAllKiosks() {
        return kioskRepository.findAll();
    }

    @Override
    public String readFileFromClassPath(String filename) throws IOException {
        ClassPathResource resource = new ClassPathResource(filename); // 클래스패스 기준
        Path path = resource.getFile().toPath();
        return Files.readString(path); // 파일 내용 읽기
    }

    @Override
    public Long register(Menu menu) {
        Long id = kioskRepository.save(menu).getId();

        return id;
    }

    @Override
    @Transactional
    public void saveOrder(OrderRequest orderRequest) {
        log.info("Saving order: " + orderRequest);
        // 주문 저장
        Order order = new Order();
        order.setTotal(orderRequest.calculateTotalPrice());
        order = orderRepository.save(order);

        // 주문 상세 저장
        for (OrderItemRequest item : orderRequest.getItems()) {
            OrderDetail orderDetail = new OrderDetail();
            orderDetail.setOrderId(order.getId());
            orderDetail.setMenuId(item.getMenuId());
            orderDetail.setAmount(item.getQuantity());
            orderDetail.setPrice(item.getTotalPrice());
            orderDetail.setAddCheese(item.getToppings().contains("치즈"));
            orderDetail.setAddTuna(item.getToppings().contains("참치"));
            orderDetail.setAddKimchi(item.getToppings().contains("김치"));
            orderDetail.setNapkin(item.isNapkin());
            orderDetailRepository.save(orderDetail);
        }
    }


}
