package org.opensw.kiosk.service;

import org.opensw.kiosk.entity.Menu;
import org.opensw.kiosk.entity.OrderRequest;

import java.io.IOException;
import java.util.List;

public interface KioskService {
    public List<Menu> getAllKiosks();
    public String readFileFromClassPath(String filename) throws IOException;

    public Long register(Menu menu);

    public void saveOrder(OrderRequest orderRequest);
}
