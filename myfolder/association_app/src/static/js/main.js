// 主脚本文件
// 创建Vue应用

// 定义组件
const 主页 = { 
    template: `<h2>欢迎来到活动报名系统</h2><p>请选择左侧导航进行操作。</p>` 
};

const Login = { 
    template: `
    <div>
        <h2>登录</h2>
        <form @submit.prevent="doLogin">
            <div class="mb-3"><label>用户名<input v-model="username" class="form-control"></label></div>
            <div class="mb-3"><label>密码<input type="password" v-model="password" class="form-control"></label></div>
            <button class="btn btn-primary">登录</button>
        </form>
    </div>`,
    data() { 
        return { 
            username:'', 
            password:'' 
        }; 
    },
    methods: {
        async doLogin() {
            try {
                const resp = await axios.post('/api/auth/login', {
                    username: this.username,
                    password: this.password
                });
                localStorage.setItem('token', resp.data.token);
                axios.defaults.headers.common['Authorization'] = 'Bearer ' + resp.data.token;
                this.$router.push('/activities');
            } catch(e) {
                alert('登录失败');
            }
        }
    }
};

const Register = {
    template: `
    <div>
        <h2>注册</h2>
        <form @submit.prevent="doRegister">
            <div class="mb-3"><label>用户名<input v-model="username" class="form-control"></label></div>
            <div class="mb-3"><label>邮箱<input v-model="email" class="form-control"></label></div>
            <div class="mb-3"><label>密码<input type="password" v-model="password" class="form-control"></label></div>
            <button class="btn btn-primary">注册</button>
        </form>
    </div>`,
    data() {
        return {
            username:'',
            email:'',
            password:''
        };
    },
    methods: {
        async doRegister() {
            try {
                await axios.post('/api/auth/register', {
                    username: this.username,
                    email: this.email,
                    password: this.password
                });
                alert('注册成功，请登录');
                this.$router.push('/login');
            } catch(e) {
                alert('注册失败');
            }
        }
    }
};

const Activities = {
    template: `
    <div>
        <h2>活动列表</h2>
        <ul class="list-group">
            <li v-for="act in activities" :key="act.id" class="list-group-item">
                <strong>{{ act.title }}</strong>
                <button class="btn btn-sm btn-success float-end" @click="signUp(act.id)">报名</button>
                <p>{{ act.description }}</p>
            </li>
        </ul>
    </div>`,
    data() {
        return {
            activities: []
        };
    },
    async created() {
        try {
            const resp = await axios.get('/api/activities');
            // 后端返回 { success, activities: [...], ... }
            this.activities = resp.data.activities;
        } catch(e) {
            console.error('获取活动列表失败', e);
        }
    },
    methods: {
        async signUp(id) {
            try {
                // 对应后端 /api/registration/activities/:id/register
                await axios.post(`/api/registration/activities/${id}/register`);
                alert('报名成功');
            } catch(e) {
                alert('报名失败');
            }
        }
    }
};

const MyRegistrations = {
    template: `
    <div>
        <h2>我的报名</h2>
        <ul class="list-group">
            <li v-for="item in regs" :key="item.registration.id" class="list-group-item">
                活动: {{ item.activity.title }} 
                <br>状态: {{ item.registration.status }} 
                <br>时间: {{ item.registration.registration_time || item.registration.timestamp }}
            </li>
        </ul>
    </div>`,
    data() {
        return {
            regs: []
        };
    },
    async created() {
        try {
            // 对应后端 /api/registration/my-registrations
            const resp = await axios.get('/api/registration/my-registrations');
            // 后端返回 { success, registrations: [ { registration, activity }, ... ] }
            this.regs = resp.data.registrations;
        } catch(e) {
            console.error('获取报名记录失败', e);
        }
    }
};

const Profile = {
    template: '<div><h2>个人资料</h2><p>功能待完善</p></div>'
};

const Admin = {
    template: '<div><h2>管理面板</h2><p>功能待完善</p></div>'
};

// 路由配置
const routes = [
    { path: '/', component: 主页 },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/activities', component: Activities },
    { path: '/my-registrations', component: MyRegistrations },
    { path: '/profile', component: Profile },
    { path: '/admin', component: Admin }
];

// 创建路由实例
const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes
});

// 全局初始化：带上 token
const token = localStorage.getItem('token');
if (token) {
    axios.defaults.headers.common['Authorization'] = 'Bearer ' + token;
}

// 创建Vue应用实例
const app = Vue.createApp({
    data() {
        return {
            currentUser: null,
            toastTitle: '',
            toastMessage: '',
            toastClass: 'bg-primary text-white'
        };
    },
    async created() {
        try {
            const resp = await axios.get('/api/auth/me');
            this.currentUser = resp.data;
        } catch(e) {
            console.log('未登录或会话已过期');
        }
    },
    methods: {
        logout() {
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            this.currentUser = null;
            this.$router.push('/');
        },
        showToast(title, message, type = 'primary') {
            this.toastTitle = title;
            this.toastMessage = message;
            this.toastClass = `bg-${type} text-white`;
            const toastEl = this.$refs.toast;
            if (toastEl) {
                const toast = new bootstrap.Toast(toastEl);
                toast.show();
            }
        }
    }
});

// 使用路由插件并挂载应用
app.use(router);
app.mount('#app');
