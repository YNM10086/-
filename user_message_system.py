from pymysql import Connection
import sys  # 全局变量sys_num_choice = None

id_key = None

# 数据库连接配置 - 建议生产环境放在配置文件
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'XXXXXXXXXX', # 密码由自己设置
    'charset': 'utf8mb4'
}
# 数据库名
DB_NAME = 'new_system'
# 管理员密钥
MANAGER_KEY = 'XXXXXXXXX'  # 密码由自己设置


def get_connection():
    """获取数据库连接"""
    try:
        conn = Connection(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)


def sys_begin():
    """系统主菜单"""
    global sys_num_choice
    print('\n###欢迎使用本系统###')
    print('#1 信息录入')
    print('#2 信息查询、修改')
    print('#3 管理员模式')
    print('#4 退出')

    # 主菜单输入验证
    while True:
        try:
            sys_num_choice = int(input('请输入您所需的服务(1-4):'))
            if 1 <= sys_num_choice <= 4:
                break
            else:
                print('输入超出范围，请重新输入1-4的数字')
        except ValueError:
            print('输入格式错误，请输入数字')


def check_key():
    """密码确认函数（复用）"""
    global id_key
    while True:
        id = input('请输入你的账号ID：')
        id_key = input('请设置账号密码：')
        id_key_1 = input('请确认密码：')

        if id_key == id_key_1:
            print('密码设置成功！')
            return id, id_key
        else:
            print('两次输入的密码不一致，请重新设置！')


def validate_info(name, age, gender, job):
    """个人信息验证函数"""
    errors = []
    # 姓名验证
    if not name or len(name.strip()) == 0:
        errors.append("姓名不能为空")
    # 年龄验证
    try:
        age_int = int(age)
        if age_int < 0 or age_int > 150:
            errors.append("年龄必须在0-150之间")
    except ValueError:
        errors.append("年龄必须为数字")
    # 性别验证
    if gender not in ['男', '女', '其他']:
        errors.append("性别请输入 男/女/其他")
    # 职业验证
    if not job or len(job.strip()) == 0:
        errors.append("职业不能为空")
    return errors


def register_info():
    """信息录入模块"""
    print('\n--- 信息录入模块 ---')
    # 1. 账号密码注册
    id, id_key = check_key()

    # 2. 个人信息录入+验证
    while True:
        info_input = input('请输入您的姓名、年龄、性别、职业，并用空格隔开：')
        info_list = info_input.strip().split()
        if len(info_list) != 4:
            print(f'输入数量错误！需要4项信息，您输入了{len(info_list)}项，请重新输入')
            continue

        name, age, gender, job = info_list
        errors = validate_info(name, age, gender, job)
        if errors:
            print('信息录入格式错误：')
            for err in errors:
                print(f'- {err}')
            print('请重新输入所有信息')
            continue

        # 验证通过，显示预览
        break

    # 3. 信息预览与确认
    print('\n--- 信息预览 ---')
    print(f'账号为：{id}')
    print(f'密码为：{id_key}')
    print(f'姓名为：{name}')
    print(f'年龄为：{age}')
    print(f'性别为:{gender}')
    print(f'职业为：{job}')

    while True:
        check_choice = input('\n请确认是否导入信息，1、是 2、否：')
        if check_choice in ['1', '2']:
            check_choice = int(check_choice)
            break
        else:
            print('输入无效，请输入1或2')

    if check_choice == 1:
        try:
            conn = get_connection()
            conn.select_db(DB_NAME)
            cursor = conn.cursor()

            # 获取最大num
            cursor.execute('select max(num) from message_system')
            result = cursor.fetchone()
            max_num = result[0]
            num = 1 if max_num is None else max_num + 1

            # 插入数据
            cursor.execute(
                "insert into message_system(num,id,id_key,name,age,gender,job) values(%s,%s,%s,%s,%s,%s,%s)",
                (num, id, id_key, name, int(age), gender, job)
            )
            conn.commit()
            print('✅ 信息录入成功')
        except Exception as e:
            print(f'❌ 信息录入失败: {e}')
            conn.rollback() if 'conn' in locals() else None
        finally:
            cursor.close() if 'cursor' in locals() else None
            conn.close() if 'conn' in locals() else None
    else:
        print('❌ 操作已经取消')


def query_modify_info():
    """信息查询、修改模块"""
    print('\n--- 信息查询、修改模块 ---')
    a = None
    conn = get_connection()
    conn.select_db(DB_NAME)
    cursor = conn.cursor()

    while a == None:
        id = input('请输入需要查询的账号(退出请输入q)：')
        if id == 'q':
            print('已退出')
            break

        try:
            # 查询账号是否存在
            cursor.execute('select id_key from message_system where id = %s', (id,))
            result = cursor.fetchone()
            if not result:
                print('❌ 用户名不存在')
                continue

            result_1 = result[0]
            print('✅ 用户名存在')
            id_key_input = input('请输入密码：')

            if id_key_input == result_1:
                print('✅ 密码正确！')

                # 查询并显示用户信息
                cursor.execute('select name,age,gender,job from message_system where id = %s', (id,))
                result_2 = cursor.fetchone()
                name, age, gender, job = result_2
                print(f'用户信息为：姓名={name}, 年龄={age}, 性别={gender}, 职业={job}')

                # 修改选项
                while True:
                    update_choice = input('输入1修改数据，0退出：')
                    if update_choice in ['1', '0']:
                        update_choice = int(update_choice)
                        break
                    else:
                        print('输入无效，请输入1或0')

                if update_choice == 1:
                    # 修改信息验证
                    while True:
                        update_input = input('请输入修改后的姓名、年龄、性别、职业，并用空格隔开：')
                        update_list = update_input.strip().split()
                        if len(update_list) != 4:
                            print(f'输入数量错误！需要4项信息，您输入了{len(update_list)}项，请重新输入')
                            continue

                        new_name, new_age, new_gender, new_job = update_list
                        errors = validate_info(new_name, new_age, new_gender, new_job)
                        if errors:
                            print('修改信息格式错误：')
                            for err in errors:
                                print(f'- {err}')
                            print('请重新输入所有修改信息')
                            continue
                        break

                    # 执行修改
                    try:
                        cursor.execute(
                            'update message_system set name = %s, age = %s, gender = %s, job = %s where id = %s',
                            (new_name, int(new_age), new_gender, new_job, id)
                        )
                        conn.commit()
                        print('✅ 信息修改完毕')
                    except Exception as e:
                        print(f'❌ 信息修改失败: {e}')
                        conn.rollback()
                a = 0
            else:
                print('❌ 密码错误')

        except Exception as e:
            print(f'❌ 查询失败: {e}')
    cursor.close()
    conn.close()


def admin_login():
    """管理员密码检查"""
    print('\n--- 管理员登录 ---')
    manager_1 = None
    while manager_1 == None:
        manager_key_1 = input('请输入管理员密码：')
        if MANAGER_KEY == manager_key_1:
            print('✅ 密码正确！')
            return True
        else:
            print('❌ 密码错误')
            while True:
                manager_2 = input('是否重新输入1、是 2、否：')
                if manager_2 in ['1', '2']:
                    manager_2 = int(manager_2)
                    break
                else:
                    print('输入无效，请输入1或2')
            if manager_2 == 1:
                continue
            else:
                return False


def admin_search_without_pwd(cursor):
    """管理员查询指定账号（无需密码）- 支持按序号/账号/姓名查询"""
    while True:
        search_input = input('请输入需要查询的序号/账号/姓名(退出子查询请输入q)：')
        if search_input == 'q':
            break
        try:
            # 先尝试按序号(num)查询，如果输入是数字的话
            if search_input.isdigit():
                cursor.execute('select * from message_system where num = %s', (search_input,))
                result = cursor.fetchone()
                if result:
                    display_account_info(result)
                    continue

            # 再按账号(id)查询
            cursor.execute('select * from message_system where id = %s', (search_input,))
            result = cursor.fetchone()
            if result:
                display_account_info(result)
                continue

            # 最后按姓名(name)查询
            cursor.execute('select * from message_system where name = %s', (search_input,))
            results = cursor.fetchall()
            if results:
                if len(results) == 1:
                    display_account_info(results[0])
                else:
                    print(f'\n找到 {len(results)} 个同名账号：')
                    for idx, row in enumerate(results, 1):
                        print(f'{idx}. 序号={row[0]}, 账号={row[1]}, 姓名={row[3]}')
                continue

            # 都没找到
            print('❌ 该账号/姓名/序号不存在')

        except Exception as e:
            print(f'❌ 查询失败: {e}')


def display_account_info(result):
    """显示账号完整信息"""
    print('\n--- 账号全信息 ---')
    print(f'序号: {result[0]}')
    print(f'账号: {result[1]}')
    print(f'密码: {result[2]}')
    print(f'姓名: {result[3]}')
    print(f'年龄: {result[4]}')
    print(f'性别: {result[5]}')
    print(f'职业: {result[6]}')


def admin_list_all(cursor):
    """管理员功能1：列出所有账号名+总数，附子查询"""
    try:
        # 查账号总数
        cursor.execute('select count(*) from message_system')
        total_count = cursor.fetchone()[0]
        # 查所有账号信息（序号、姓名、账号）
        cursor.execute('select num, name, id from message_system order by num')
        account_list = cursor.fetchall()

        print(f'\n--- 所有账号统计 ---')
        print(f'✅ 账号总数: {total_count}')
        if total_count > 0:
            print('✅ 所有账号列表:')
            for row in account_list:
                print(f'{row[0]}. 姓名: {row[1]}, 账号: {row[2]}')

        # 子菜单循环
        while True:
            sub_choice = input('\n请选择操作: 1、查询指定账号 0、返回管理员主菜单: ')
            if sub_choice == '1':
                admin_search_without_pwd(cursor)
            elif sub_choice == '0':
                break
            else:
                print('输入无效，请输入1或0')
    except Exception as e:
        print(f'❌ 获取账号列表失败: {e}')


def admin_gender_stat(cursor):
    """管理员功能2：统计男女账号数"""
    try:
        # 统计男生
        cursor.execute("select count(*) from message_system where gender = '男'")
        male_count = cursor.fetchone()[0]
        # 统计女生
        cursor.execute("select count(*) from message_system where gender = '女'")
        female_count = cursor.fetchone()[0]

        print(f'\n--- 性别统计 ---')
        print(f'✅ 男性账号数: {male_count}')
        print(f'✅ 女性账号数: {female_count}')
    except Exception as e:
        print(f'❌ 性别统计失败: {e}')


def admin_main_menu():
    """管理员主菜单"""
    conn = get_connection()
    conn.select_db(DB_NAME)
    cursor = conn.cursor()

    while True:
        print('\n--- 管理员主菜单 ---')
        print('#1 查看所有账号名+账号总数（可子查询）')
        print('#2 统计男、女账号数')
        print('#0 返回主系统菜单')

        # 管理员菜单输入验证
        while True:
            try:
                admin_choice = int(input('请选择操作(0-2): '))
                if 0 <= admin_choice <= 2:
                    break
                else:
                    print('输入超出范围，请重新输入0-2的数字')
            except ValueError:
                print('输入格式错误，请输入数字')

        if admin_choice == 1:
            admin_list_all(cursor)
        elif admin_choice == 2:
            admin_gender_stat(cursor)
        elif admin_choice == 0:
            print('已退出管理员模式')
            break

    cursor.close()
    conn.close()


def main():
    """主程序入口"""
    sys_num = 0
    while sys_num == 0:
        sys_begin()

        # 退出服务
        if sys_num_choice == 4:
            print('本次服务已结束 感谢您的使用')
            sys_num = 1
            break
        # 信息录入
        elif sys_num_choice == 1:
            register_info()
        # 信息查询修改
        elif sys_num_choice == 2:
            query_modify_info()
        # 管理员模式
        elif sys_num_choice == 3:
            if admin_login():
                admin_main_menu()


if __name__ == '__main__':
    main()
