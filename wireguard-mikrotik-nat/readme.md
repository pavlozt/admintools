# UDP hole punching with Wireguard and Mikrotik router #

A simple implementation [UDP Hole Punching](https://en.wikipedia.org/wiki/UDP_hole_punching) for wireguard on Mikrotik.

For implementation, you need one central **server with wireguard on linux** and **at least two Mikrotiks routers**. On linux, there must be a web server and the ability to publish files (for example, nginx).

The [update_web_endpoints.sh](update_web_endpoints.sh) script must be placed in cron. The script interacts with wireguard and therefore needs to be run as root.

First you need to configure wireguard and peers. Moreover, you can leave empty addresses of peers on routers. These addresses are updated by the rsc script.

The script [wg_peer_update.rsc](wg_peer_update.rsc) should be placed in Mikrotik in the System/Scripts menu.
In one of mikrotik to choose from, create a scheduler task consisting of one line:
```
:execute script="wg_peer_update"
```
and run it every 1-3 minutes.
### Warning ###
Not every provider's NAT allows you to accept "foreign" connections (that is, where the source address does not match the original destination address) as input. In this case, you can swap points. It is enough that at least one of the two providers accepts such connections.

### Critics ###
The script is a deliberate compromise between security and the speed of switching the tunnel to a new address.
Mikrotik is fully controlled by a local script and does not use remote login anywhere.
Thus, although this solution does not switch quickly, there is practically no scenario for hacking here.

If you need the fastest possible tunnel switching, I recommend coming up with a script based on the mqtt client (https://help.mikrotik.com/docs/display/ROS/MQTT) .
If you are willing to accept potential security risks, you can switch tunnels by sshing into mikrotik at the tunnel address.
However, there is no ready-made code for such a scheme in this repository.

It is desirable to supplement the scheme with dynamic routing so that the tunnels always work as intended.

There are alternative ideas here https://www.jordanwhited.com/posts/wireguard-endpoint-discovery-nat-traversal/ with pictures but the implementation only works with linux.

This solution is meant to be as simple as possible.


## На русском ##

Это простая реализация [UDP Hole Punching](https://en.wikipedia.org/wiki/UDP_hole_punching) для wireguard на Mikrotik .

Для реализации нужен один **центральный сервер с wireguard на linux** и **хотя бы два маршрутизатора Mikrotik**. На linux должен быть веб-сервер и возможность публиковать  файлы (например, nginx). В скриптах необходимо настроить публичный ключ и каталог для раздачи.

Скрипт [update_web_endpoints.sh](update_web_endpoints.sh) необходимо поместить в cron. Скрипт взаимодействует с wireguard и поэтому нуждается в запуске от root.

Предварительно нужно настроить wireguard и peers. Причем, можно оставить пустыми адреса пиров на маршрутизаторов. Эти адреса обновляются скриптом rsc.

Скрипт [wg_peer_update.rsc](wg_peer_update.rsc) следует поместить в Mikrotik в меню System/Scripts.
В одном из mikrotik на выбор создать задачу  scheduler состоящую из одной строчки:
```
:execute script="wg_peer_update"
```
и запускать ее раз в 1-3 минуты.

### Предупреждение ###
Не у каждого провайдера NAT позволяет принимать на вход "чужие" соединения (то есть, где адрес источника не совпадает с изначальным адресом назначения).
В этом случае можно поменять местами точки. Достаточно чтобы хотя бы один из двух провайдеров принимал такие соединения.

### Критика ###
Скрипт представляет собой осознанный компромисс между безопасностью и скоростью переключения туннеля на новый адрес.
Mikrotik полностью контроллируется локальным скриптом и нигде не используется удаленный вход.
Таким образом, это решение хоть и не переключается оперативно, но сценарие для взлома тут практически нет.

Если вам нужно максимально быстрое переключение туннелей, порекомендую придумать скрипт на основе mqtt-клиента (https://help.mikrotik.com/docs/display/ROS/MQTT) .
Если вы готовы пойти на потенциальные риски  безопасности, можете переключать туннели с помощью входа на mikrotik через ssh по туннельному адресу.
Однако, в этом репозитарии нет готового кода для такой схемы.

Желательно дополнить схему динамической маршрутизацией, чтобы туннели всегда работали по назначению.

Здесь есть альтернативные идеи https://www.jordanwhited.com/posts/wireguard-endpoint-discovery-nat-traversal/, объяснения с картинками, но реализация работает только с linux.

Это решение задумано быть максимально простым.