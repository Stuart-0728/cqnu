// 主脚本文件
// 创建Vue应用
const app = Vue.createApp({
    data() {
        return {
            currentUser: null,
            isAdmin: false,
            toastTitle: '',
            toastMessage: '',
            toastClass: '',
            activeTab: 'activities'
        };
    },
    computed: {
        isLoggedIn() {
            return this.currentUser !== null;
        }
    },
    methods: {
        // 显示提示消息
        showToast(title, message, type) {
            this.toastTitle = title;
            this.toastMessage = message;
            this.toastClass = type === 'error' ? 'bg-danger' : type === 'warning' ? 'bg-warning' : 'bg-success';
            
            const toastEl = new bootstrap.Toast(this.$refs.toast);
            toastEl.show();
        },
        
        // 登录方法
        async login(username, password) {
            try {
                const response = await axios.post('/api/login', { username, password });
                if (response.data.success) {
                    this.currentUser = response.data.user;
                    this.isAdmin = this.currentUser.role === 'admin';
                    this.showToast('成功', '登录成功', 'success');
                    
                    // 如果是管理员，跳转到管理面板
                    if (this.isAdmin) {
                        window.location.href = '/admin';
                    } else {
                        window.location.href = '/';
                    }
                } else {
                    this.showToast('错误', response.data.message || '登录失败', 'error');
                }
            } catch (error) {
                console.error('登录失败:', error);
                this.showToast('错误', '登录失败', 'error');
            }
        },
        
        // 注册方法
        async register(userData) {
            try {
                const response = await axios.post('/api/register', userData);
                if (response.data.success) {
                    this.showToast('成功', '注册成功，请登录', 'success');
                    // 跳转到登录页面
                    window.location.href = '/login';
                } else {
                    this.showToast('错误', response.data.message || '注册失败', 'error');
                }
            } catch (error) {
                console.error('注册失败:', error);
                this.showToast('错误', '注册失败', 'error');
            }
        },
        
        // 登出方法
        async logout() {
            try {
                const response = await axios.post('/api/logout');
                if (response.data.success) {
                    this.currentUser = null;
                    this.isAdmin = false;
                    this.showToast('成功', '已安全登出', 'success');
                    window.location.href = '/';
                } else {
                    this.showToast('错误', '登出失败', 'error');
                }
            } catch (error) {
                console.error('登出失败:', error);
                this.showToast('错误', '登出失败', 'error');
            }
        },
        
        // 检查用户登录状态
        async checkLoginStatus() {
            try {
                const response = await axios.get('/api/user/current');
                if (response.data.success && response.data.user) {
                    this.currentUser = response.data.user;
                    this.isAdmin = this.currentUser.role === 'admin';
                }
            } catch (error) {
                console.error('获取用户信息失败:', error);
            }
        }
    },
    mounted() {
        // 页面加载时检查登录状态
        this.checkLoginStatus();
    }
});

// 登录组件
app.component('login-form', {
    template: `
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">用户登录</h3>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="submitLogin">
                                <div class="mb-3">
                                    <label for="username" class="form-label">用户名</label>
                                    <input type="text" class="form-control" id="username" v-model="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">密码</label>
                                    <input type="password" class="form-control" id="password" v-model="password" required>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary">登录</button>
                                </div>
                            </form>
                            <div class="mt-3 text-center">
                                <p>还没有账号？ <a href="/register">立即注册</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            username: '',
            password: ''
        };
    },
    methods: {
        submitLogin() {
            this.$root.login(this.username, this.password);
        }
    }
});

// 注册组件
app.component('register-form', {
    template: `
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">用户注册</h3>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="submitRegister">
                                <div class="mb-3">
                                    <label for="username" class="form-label">用户名</label>
                                    <input type="text" class="form-control" id="username" v-model="userData.username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="email" class="form-label">邮箱</label>
                                    <input type="email" class="form-control" id="email" v-model="userData.email" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">密码</label>
                                    <input type="password" class="form-control" id="password" v-model="userData.password" required>
                                </div>
                                <div class="mb-3">
                                    <label for="confirmPassword" class="form-label">确认密码</label>
                                    <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required>
                                </div>
                                <div class="mb-3">
                                    <label for="fullName" class="form-label">姓名</label>
                                    <input type="text" class="form-control" id="fullName" v-model="userData.full_name" required>
                                </div>
                                <div class="d-grid">
                                    <button type="submit" class="btn btn-primary" :disabled="!isFormValid">注册</button>
                                </div>
                            </form>
                            <div class="mt-3 text-center">
                                <p>已有账号？ <a href="/login">立即登录</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            userData: {
                username: '',
                email: '',
                password: '',
                full_name: ''
            },
            confirmPassword: ''
        };
    },
    computed: {
        isFormValid() {
            return this.userData.password && this.userData.password === this.confirmPassword;
        }
    },
    methods: {
        submitRegister() {
            if (!this.isFormValid) {
                this.$root.showToast('错误', '两次输入的密码不一致', 'error');
                return;
            }
            this.$root.register(this.userData);
        }
    }
});

// 活动详情组件
const ActivityDetail = {
    template: `
    <div class="container" v-if="activity">
        <div class="row">
            <div class="col-md-8">
                <h2 class="mb-3">{{ activity.title }}</h2>
                <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="img-fluid rounded mb-4">
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">活动详情</h5>
                        <p class="card-text">{{ activity.description }}</p>
                    </div>
                </div>
                <div>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item">开始时间: {{ formatDate(activity.start_time) }}</li>
                        <li class="list-group-item">结束时间: {{ formatDate(activity.end_time) }}</li>
                        <li class="list-group-item">地点: {{ activity.location }}</li>
                        <li class="list-group-item">状态: {{ getStatusText(activity.status) }}</li>
                    </ul>
                </div>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary w-100" @click="registerActivity" 
                        :disabled="activity.status !== 'active' || isRegistered">
                    {{ isRegistered ? '已报名' : '立即报名' }}
                </button>
            </div>
        </div>
    </div>
    <div v-else>
        <div class="container text-center py-5" v-else>
            <p>加载中...</p>
        </div>
    </div>
    `,
    data() {
        return {
            activity: null,
            isRegistered: false,
            activityId: ''
        };
    },
    methods: {
        async fetchActivityDetail() {
            if (!this.activityId) return;
            
            try {
                const response = await axios.get(`/api/activities/${this.activityId}`);
                this.activity = response.data.activity;
            } catch (error) {
                console.error('获取活动详情失败:', error);
                app.showToast('错误', '获取活动详情失败', 'error');
            }
        },
        
        async checkRegistrationStatus() {
            if (!app.isLoggedIn || !this.activityId) return;
            
            try {
                const response = await axios.get(`/api/activities/${this.activityId}/registration`);
                this.isRegistered = response.data.registered;
            } catch (error) {
                console.error('检查报名状态失败:', error);
            }
        },
        
        async registerActivity() {
            if (!app.isLoggedIn) {
                app.showToast('提示', '请先登录', 'warning');
                return;
            }
            
            try {
                const response = await axios.post(`/api/activities/${this.activityId}/register`);
                if (response.data.success) {
                    this.isRegistered = true;
                    app.showToast('成功', '报名成功', 'success');
                }
            } catch (error) {
                console.error('报名失败:', error);
                app.showToast('错误', '报名失败', 'error');
            }
        },
        
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        getStatusText(status) {
            const statusMap = {
                'draft': '草稿',
                'active': '进行中',
                'completed': '已结束',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        }
    },
    mounted() {
        // 从URL获取活动ID
        const pathParts = window.location.pathname.split('/');
        this.activityId = pathParts[pathParts.length - 1];
        
        this.fetchActivityDetail();
        this.checkRegistrationStatus();
    }
};

// 管理员控制面板组件
const AdminDashboard = {
    template: `
    <div class="container" v-if="isAdmin">
        <h2 class="mb-4">管理员控制面板</h2>
        <div class="row">
            <div class="col-md-3 mb-4">
                <div class="list-group">
                    <a href="#" class="list-group-item list-group-item-action"
                       :class="{ active: activeTab === 'activities' }"
                       @click.prevent="activeTab = 'activities'">
                       活动管理
                    </a>
                    <a href="#" class="list-group-item list-group-item-action"
                       :class="{ active: activeTab === 'users' }"
                       @click.prevent="activeTab = 'users'">
                       用户管理
                    </a>
                    <a href="#" class="list-group-item list-group-item-action"
                       :class="{ active: activeTab === 'registrations' }"
                       @click.prevent="activeTab = 'registrations'">
                       报名管理
                    </a>
                </div>
            </div>
            <div class="col-md-9">
                <!-- 活动管理 -->
                <div v-if="activeTab === 'activities'">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h3>活动管理</h3>
                        <a href="/activities/new" class="btn btn-primary">新建活动</a>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>标题</th>
                                    <th>开始时间</th>
                                    <th>状态</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="activity in activities" :key="activity.id">
                                    <td>{{ activity.id }}</td>
                                    <td>{{ activity.title }}</td>
                                    <td>{{ formatDate(activity.start_time) }}</td>
                                    <td>{{ getStatusText(activity.status) }}</td>
                                    <td>
                                        <div class="btn-group btn-group-sm">
                                            <a :href="'/activities/' + activity.id" class="btn btn-info">查看</a>
                                            <a :href="'/activities/' + activity.id + '/edit'" class="btn btn-warning">编辑</a>
                                            <button @click="deleteActivity(activity.id)" class="btn btn-danger">删除</button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 用户管理 -->
                <div v-if="activeTab === 'users'">
                    <h3>用户管理</h3>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>用户名</th>
                                    <th>邮箱</th>
                                    <th>角色</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="user in users" :key="user.id">
                                    <td>{{ user.id }}</td>
                                    <td>{{ user.username }}</td>
                                    <td>{{ user.email }}</td>
                                    <td>{{ user.role }}</td>
                                    <td>
                                        <button @click="toggleUserRole(user.id)" class="btn btn-warning">
                                            {{ user.role === 'admin' ? '取消管理员' : '设为管理员' }}
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- 报名管理 -->
                <div v-if="activeTab === 'registrations'">
                    <h3>报名管理</h3>
                    <div class="form-group mb-3">
                        <select id="activitySelect" class="form-control" v-model="selectedActivityId" @change="fetchRegistrations()">
                            <option value="">-- 请选择活动 --</option>
                            <option v-for="activity in activities" :key="activity.id" :value="activity.id">
                                {{ activity.title }}
                            </option>
                        </select>
                    </div>
                    <div class="table-responsive" v-if="selectedActivityId">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>用户名</th>
                                    <th>邮箱</th>
                                    <th>报名时间</th>
                                    <th>操作</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="reg in registrations" :key="reg.id">
                                    <td>{{ reg.id }}</td>
                                    <td>{{ reg.user.username }}</td>
                                    <td>{{ reg.user.email }}</td>
                                    <td>{{ formatDate(reg.created_at) }}</td>
                                    <td>
                                        <button @click="cancelRegistration(reg.id)" class="btn btn-sm btn-danger">取消报名</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div class="text-center py-3" v-if="registrations.length === 0">
                            <p>暂无报名记录</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="container text-center py-5" v-else>
        <p>您没有权限访问此页面</p>
    </div>
    `,
    data() {
        return {
            activeTab: 'activities',
            activities: [],
            users: [],
            registrations: [],
            selectedActivityId: '',
            isAdmin: app.isAdmin
        };
    },
    mounted() {
        // 确保用户是管理员
        if (this.isAdmin) {
            this.fetchActivities();
            this.fetchUsers();
        } else {
            console.log('非管理员用户尝试访问控制面板');
        }
    },
    methods: {
        async fetchActivities() {
            try {
                const response = await axios.get('/api/admin/activities');
                if (response.data.success) {
                    this.activities = response.data.activities;
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
                app.showToast('错误', '获取活动列表失败', 'error');
            }
        },
        
        async fetchUsers() {
            try {
                const response = await axios.get('/api/admin/users');
                if (response.data.success) {
                    this.users = response.data.users;
                }
            } catch (error) {
                console.error('获取用户列表失败:', error);
                app.showToast('错误', '获取用户列表失败', 'error');
            }
        },
        
        async fetchRegistrations() {
            if (!this.selectedActivityId) return;
            
            try {
                const response = await axios.get(`/api/admin/activities/${this.selectedActivityId}/registrations`);
                if (response.data.success) {
                    this.registrations = response.data.registrations;
                }
            } catch (error) {
                console.error('获取报名列表失败:', error);
                app.showToast('错误', '获取报名列表失败', 'error');
            }
        },
        
        async deleteActivity(activityId) {
            if (!confirm('确定要删除此活动吗？此操作不可逆。')) return;
            
            try {
                const response = await axios.delete(`/api/admin/activities/${activityId}`);
                if (response.data.success) {
                    app.showToast('成功', '活动已删除', 'success');
                    this.fetchActivities();
                }
            } catch (error) {
                console.error('删除活动失败:', error);
                app.showToast('错误', '删除活动失败', 'error');
            }
        },
        
        async toggleUserRole(userId) {
            try {
                const user = this.users.find(u => u.id === userId);
                const newRole = user.role === 'admin' ? 'user' : 'admin';
                
                const response = await axios.put(`/api/admin/users/${userId}/role`, { role: newRole });
                if (response.data.success) {
                    app.showToast('成功', '用户角色已更新', 'success');
                    this.fetchUsers();
                }
            } catch (error) {
                console.error('更新用户角色失败:', error);
                app.showToast('错误', '更新用户角色失败', 'error');
            }
        },
        
        async cancelRegistration(regId) {
            if (!confirm('确定要取消此报名记录吗？')) return;
            
            try {
                const response = await axios.delete(`/api/admin/registrations/${regId}`);
                if (response.data.success) {
                    app.showToast('成功', '报名已取消', 'success');
                    this.fetchRegistrations();
                }
            } catch (error) {
                console.error('取消报名失败:', error);
                app.showToast('错误', '取消报名失败', 'error');
            }
        },
        
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        
        getStatusText(status) {
            const statusMap = {
                'draft': '草稿',
                'active': '进行中',
                'completed': '已结束',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        }
    }
};

// 设置Vue路由
const routes = [
    { path: '/', component: { template: '<div>首页内容</div>' } },
    { path: '/login', component: { template: '<login-form></login-form>' } },
    { path: '/register', component: { template: '<register-form></register-form>' } },
    { path: '/activities/:id', component: ActivityDetail },
    { path: '/admin', component: AdminDashboard }
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes
});

app.use(router);

// 挂载Vue应用
app.mount('#app');
