"""
地信专业综合计算程序
功能1：中央子午线/带号双向计算（6°带、3°带）
功能2：GB/T 13989-2012 多比例尺地形图分幅编号计算（仅接受标准经纬度格式输入）
日期：2026-04
"""
import math
import re

 
# --------------------------

# --------------------------
def main_menu():
    while True:
        print("\n" + "=" * 50)
        print("地信专业综合计算程序")
        print("=" * 50)
        print("1. 中央子午线计算/带号计算")
        print("2. 地形图分幅编号的计算（GB/T 13989-2012）")
        print("0. 退出程序")
        print("=" * 50)

        choice = input("请选择选项（0-2）：")

        if choice == "1":
            zone_calculation_menu()
        elif choice == "2":
            topo_map_numbering_menu()
        elif choice == "0":
            print("感谢使用，程序已退出！")
            break
        else:
            print("无效选项，请重新选择！")


def zone_calculation_menu():
    while True:
        print("\n" + "=" * 50)
        print("中央子午线计算/带号计算")
        print("=" * 50)
        print("1. 6°带计算")
        print("2. 3°带计算")
        print("0. 返回主菜单")
        print("=" * 50)

        choice = input("请选择选项（0-2）：")

        if choice == "1":
            sub_menu("6°带")
        elif choice == "2":
            sub_menu("3°带")
        elif choice == "0":
            break
        else:
            print("无效选项，请重新选择！")


def sub_menu(zone_type):
    while True:
        print("\n" + "=" * 50)
        print(f"{zone_type}计算")
        print("=" * 50)
        print("1. 输入经度")
        print("2. 输入带号")
        print("0. 返回上一级菜单")
        print("=" * 50)

        choice = input("请选择选项（0-2）：")

        if choice == "1":
            try:
               
                longitude = float(input("请输入经度（十进制，东经为正，西经为负）："))
                if zone_type == "6°带":
                    N = math.floor(longitude / 6) + 1 if longitude >= 0 else math.ceil(longitude / 6) + 1
                    print(f"\n所在带号N= {N}")
                elif zone_type == "3°带":
                    n = round(longitude / 3)
                    print(f"\n所在带号n= {n}")
            except ValueError:
                print("请输入有效的十进制数值！")
        elif choice == "2":
            try:
                
                zone_num = int(input("请输入带号："))
                if zone_type == "6°带":
                    L = zone_num * 6 - 3
                    print(f"\n中央子午线L= {L}°")
                elif zone_type == "3°带":
                    L = zone_num * 3
                    print(f"\n中央子午线L= {L}°")
            except ValueError:
                print("请输入有效的整数带号！")
        elif choice == "0":
            break
        else:
            print("无效选项，请重新选择！")


# --------------------------

# --------------------------
def topo_map_numbering_menu():
    """地形图分幅编号主入口"""
    while True:
        print("\n" + "=" * 50)
        print("地形图分幅编号的计算（GB/T 13989-2012）")
        print("=" * 50)
        print("1. 输入经纬度计算多比例尺图幅编号")
        print("0. 返回主菜单")
        print("=" * 50)
        print("提示：经纬度输入格式示例：116°3'45\" E 或 39°54'23\" N")
        print("=" * 50)

        choice = input("请选择选项（0-1）：")

        if choice == "1":
            # 仅接受标准经纬度格式输入
            lon_str = input("\n请输入经度（格式示例：116°3'45\" E 或 89°12'34\" W）：")
            lat_str = input("请输入纬度（格式示例：39°54'23\" N 或 23°45'6\" S）：")

            # 解析经纬度
            lon = parse_dms_to_decimal(lon_str, "经度")
            lat = parse_dms_to_decimal(lat_str, "纬度")

            # 仅解析成功才计算
            if lon is not None and lat is not None:
                calculate_all_scales(lon, lat)
        elif choice == "0":
            break
        else:
            print("无效选项，请重新选择！")


def parse_dms_to_decimal(dms_str, coord_type):
    """
    解析标准度分秒格式字符串为十进制数值
    支持格式：DDD°MM'SS.ss\" E/W/N/S 或 DD°MM'SS\" E/W/N/S（注意秒用双引号）
    """
    # 正则表达式匹配度分秒方向
    pattern = re.compile(
        r'^\s*(\d{1,3})°(\d{1,2})\'(\d{1,2}(?:\.\d+)?)"\s*([EWNS])\s*$',
        re.IGNORECASE
    )

    match = pattern.match(dms_str)
    if not match:
        print(f"\n错误：{coord_type}格式无效！请严格按照示例格式输入。")
        return None

    # 提取匹配到的组
    d = int(match.group(1))
    m = int(match.group(2))
    s = float(match.group(3))
    direction = match.group(4).upper()

    # 验证度分秒数值有效性
    if coord_type == "经度":
        if not (0 <= d <= 180):
            print(f"\n错误：经度度数必须在0-180之间！")
            return None
        if d == 180 and (m != 0 or s != 0):
            print(f"\n错误：经度180°时，分秒必须为0！")
            return None
    else:  # 纬度
        if not (0 <= d <= 90):
            print(f"\n错误：纬度度数必须在0-90之间！")
            return None
        if d == 90 and (m != 0 or s != 0):
            print(f"\n错误：纬度90°时，分秒必须为0！")
            return None

    if not (0 <= m < 60):
        print(f"\n错误：{coord_type}分数必须在0-59之间！")
        return None
    if not (0 <= s < 60):
        print(f"\n错误：{coord_type}秒数必须在0-59.999...之间！")
        return None

    # 转换为十进制
    decimal = d + m / 60 + s / 3600
    if direction in ['W', 'S']:
        decimal = -decimal

    return decimal


def calculate_all_scales(lon, lat):
    """【修正版】计算并输出所有7种比例尺的图幅编号（遵循GB/T 13989-2012）"""
    # 比例尺定义：(名称, 比例尺码, 经度差(度), 纬度差(度))
    scales = [
        ("1:100万", "", 6, 4),
        ("1:50万", "B", 3, 2),
        ("1:25万", "C", 1.5, 1),
        ("1:10万", "D", 0.5, 20 / 60),  # 20分
        ("1:5万", "E", 0.25, 10 / 60),  # 10分
        ("1:2.5万", "F", 0.125, 5 / 60),  # 5分
        ("1:1万", "G", 0.0625, 2.5 / 60)  # 2.5分
    ]

    base_row, base_col = calculate_100w(lon, lat)
    base_row_char = chr(ord('A') + base_row - 1)  # A对应1

    print("\n" + "-" * 60)
    print(f"输入点的十进制经纬度：经度 {lon:.6f}°，纬度 {lat:.6f}°")
    print("-" * 60)
    print(f"{'比例尺':<10} {'图幅编号':<20}")
    print("-" * 60)

    # 逐个计算其他比例尺
    for name, code, delta_lon, delta_lat in scales:
        if name == "1:100万":
            # 南半球行号加'
            current_base_row_char = base_row_char if lat >= 0 else f"{base_row_char}'"
            number = f"{current_base_row_char}{base_col:02d}"
        else:
            # 西北角纬度 = 行号 * 4°（北半球）
            # 西北角经度 = (列号 - 1) * 6° - 180°（从180°W起算）
            abs_lat = abs(lat)
            nw_lat_100w = base_row * 4  # 1:100万图幅的北界纬度
            nw_lon_100w = (base_col - 1) * 6 - 180  # 1:100万图幅的西界经度

            # 纬度偏移：从北向南减小 → 偏移 = 西北角纬度 - 当前点纬度
            # 经度偏移：从西向东增大 → 偏移 = 当前点经度 - 西北角经度
            offset_lat_sec = int(round((nw_lat_100w - abs_lat) * 3600, 6))
            offset_lon_sec = int(round((lon - nw_lon_100w) * 3600, 6))

            # 比例尺的经纬度差也转为秒
            delta_lat_sec = int(round(delta_lat * 3600, 6))
            delta_lon_sec = int(round(delta_lon * 3600, 6))

            # 行号：从北向南数 → 行数 = floor(纬度偏移 / delta_lat) + 1
            # 列号：从西向东数 → 列数 = floor(经度偏移 / delta_lon) + 1
            row = offset_lat_sec // delta_lat_sec + 1
            col = offset_lon_sec // delta_lon_sec + 1

            # 拼接编号
            current_base_row_char = base_row_char if lat >= 0 else f"{base_row_char}'"
            number = f"{current_base_row_char}{base_col:02d}{code}{row:03d}{col:03d}"

        print(f"{name:<10} {number:<20}")
    print("-" * 60)


def calculate_100w(lon, lat):
    """【修正版】计算1:100万比例尺的行号和列号（严格遵循GB/T 13989-2012）"""
    abs_lat = abs(lat)

    row = int(abs_lat // 4) + 1

    # 公式：列号 = int((经度 + 180) / 6) + 1
    col = int((lon + 180) / 6) + 1

    return row, col


if __name__ == "__main__":
    print("欢迎使用地信专业综合计算程序！")
    main_menu()

