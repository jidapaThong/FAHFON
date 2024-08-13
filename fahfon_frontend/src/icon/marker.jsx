import L, {icon} from 'leaflet';
import greenIcon from "./green_pin.png";
import redIcon from "./red_pin.png";
import blueIcon from "./blue_pin.png";
const activeIcon = L.icon({
    iconUrl: greenIcon,
    iconSize: [26, 39],
});

const inactiveIcon = L.icon({
    iconUrl: redIcon,
    iconSize: [26, 39],
});

const selectedIcon = L.icon({
    iconUrl: blueIcon,
    iconSize: [55, 55],
})

export {activeIcon, inactiveIcon, selectedIcon}